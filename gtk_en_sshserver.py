#!/bin/python3

from gi.repository import Gtk


class InterfaceModule(Gtk.Box):

    def __init__(self, menu_entry):
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_info_tab(),
            self.ui_settings()
        ]
        return ui

    @staticmethod
    def ui_info_tab():
        box = Gtk.Box()
        return box

    @staticmethod
    def ui_settings():
        box = Gtk.Box()
        return box