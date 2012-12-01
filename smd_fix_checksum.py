#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#Name: smd_fix_checksum.py
#Version (last modification): 12.11.2009
#Copyright (c) 2009 Boris Timofeev <mashin87@gmail.com> www.emunix.org
#License: GNU GPL v3

import os, shutil
import pygtk
pygtk.require('2.0')
import gtk

class SmdFixChecksum:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("SMD Fix Checksum")
        self.window.set_border_width(5)
        self.window.connect("delete_event", self.close_app)

        self.table = gtk.Table(5, 4, True)
        self.table.set_row_spacings(2)
        self.table.set_col_spacings(2)
        self.window.add(self.table)

        self.label = gtk.Label("Select ROM file:")
        self.label.set_alignment(0, 0)
        self.table.attach(self.label, 0, 4, 0, 1)

        self.textEntry = gtk.Entry()
        self.openFileButton = gtk.Button("Open file..", gtk.STOCK_OPEN)
        self.openFileButton.connect("clicked", self.select_file)

        self.backupCheckBox = gtk.CheckButton("Create a backup file.")
        self.table.attach(self.backupCheckBox, 0, 4, 2, 3)
        self.table.attach(self.textEntry, 0, 3, 1, 2)
        self.table.attach(self.openFileButton, 3, 4, 1, 2)

        self.progressbar = gtk.ProgressBar()
        self.progressbar.set_text("0%")
        self.table.attach(self.progressbar, 0, 4, 3, 4)

        self.fixButton = gtk.Button("Execute", gtk.STOCK_EXECUTE)
        self.fixButton.connect("clicked", self.smd_fix_checksum)
        self.exitButton = gtk.Button("Exit", gtk.STOCK_QUIT)
        self.exitButton.connect("clicked", self.close_app)
   
        self.table.attach(self.fixButton, 2, 3, 4, 5)
        self.table.attach(self.exitButton, 3, 4, 4, 5)

        self.window.show_all()

    def main(self):
        gtk.main()

    def close_app(self, widget, data=None):
        gtk.main_quit()

    def select_file(self, widget):
        dialog = gtk.FileChooserDialog("Open..", None, \
                gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, \
                gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.set_name("Sega Mega Drive ROMs (*.bin, *.gen)")
        filter.add_pattern("*.bin")
        filter.add_pattern("*.gen")
        dialog.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        if dialog.run() == gtk.RESPONSE_OK:
            self.textEntry.set_text(dialog.get_filename())
            self.progressbar.set_text("0%")
            self.progressbar.set_fraction(0)
        dialog.destroy()

    def error_message(self, message):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL |
gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, message)
        dialog.set_title("Error")
        if dialog.run() == gtk.RESPONSE_CLOSE:
            dialog.destroy()

    def smd_fix_checksum(self, widget):
        romfile = self.textEntry.get_text()
        if self.backupCheckBox.get_active():
            try:
                shutil.copyfile(romfile, romfile + ".bak")
            except:
                self.error_message("Can't create a backup file!")
                return
        try:
            rom = open(romfile, "r+")
        except IOError:
            self.error_message("File %s not found!" % romfile)
            return
        checksum = 0
        romsize = os.path.getsize(romfile)
        rom.seek(512)
        dBuffer = rom.read(5120)
        buffer_i = 0
        while dBuffer != "":
            data = dBuffer[0:2]
            while data != "":
                try:
                    checksum += ord(data[0:1]) * 256 + ord(data[1:2])
                except:
                    self.error_message("Error calculations")
                    rom.close()
                    return
                buffer_i += 2
                data = dBuffer[buffer_i:buffer_i+2]
            while gtk.events_pending():
                gtk.main_iteration()
            pb_percent = ((rom.tell()*100)/romsize)
            self.progressbar.set_fraction(pb_percent/100.)
            self.progressbar.set_text(unicode(pb_percent) + "%")
            buffer_i = 0
            dBuffer = rom.read(5120)
        rom.seek(0x18e)
        try:
            rom.write(chr((checksum & 0xff00)/256))
            rom.write(chr(checksum & 0xff))
        except IOError:
            self.error_message("Error writing file")
            rom.close()
            return
        rom.close()

if __name__ == "__main__":
    app = SmdFixChecksum()
    app.main()
