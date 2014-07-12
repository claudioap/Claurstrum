#!/bin/python3
from gi.repository import Gtk


class InterfaceModule(Gtk.Box):

    def __init__(self, menu_entry):
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_info_tab()
        ]
        return ui

    @staticmethod
    def ui_info_tab():
        box = Gtk.Box()
        label = Gtk.Label("This is the info tab")
        box.pack_start(label, True, True, 0)
        return box

    def connect_self_to_nb(self):
        self.notebook.interface_module = self

    def open_config(self, file):
        pass