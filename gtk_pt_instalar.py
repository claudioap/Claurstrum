#!/bin/python3
from gi.repository import Gtk


class InterfaceModule(Gtk.Box):

    def __init__(self):
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_info_tab()
        ]
        return ui

    @staticmethod
    def ui_info_tab():
        box = Gtk.Box()
        label = Gtk.Label("Este é o separador da informação")
        box.pack_start(label, True, True, 0)
        return box
