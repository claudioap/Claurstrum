#!/bin/python3
import GTKUI
import os
from gi.repository import Gtk

if os.environ.get('DESKTOP_SESSION') is None:
    pass  # This will later be used to build a TUI
else:
    UI = GTKUI.MainWindow()
    UI.connect("delete-event", Gtk.main_quit)
    UI.show_all()
    Gtk.main()

print("Ok, ok... I give up!")
