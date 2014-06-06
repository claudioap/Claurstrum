#!/bin/python3
from gi.repository import Gtk


class InterfaceModule(Gtk.Box):
    def __init__(self):
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_begin_tab(),
            self.ui_introduction_tab(),
            self.ui_usage_tab()
        ]
        return ui

    @staticmethod
    def ui_begin_tab():
        box = Gtk.Box()
        label = Gtk.Label(
            "This program welcomes you!\n\tNavigate using the tabs on the top"
        )
        box.pack_start(label, True, True, 0)
        return box

    @staticmethod
    def ui_introduction_tab():
        box = Gtk.Box()
        label = Gtk.Label("This is the introduction tab")
        box.pack_start(label, True, True, 0)
        return box

    @staticmethod
    def ui_usage_tab():
        box = Gtk.Box()
        label = Gtk.Label("This is the usage tab")
        box.pack_start(label, True, True, 0)
        return box