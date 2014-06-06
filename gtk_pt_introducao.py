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
            "O programa dá-lhe as boas vindas!\n\tNavegue utilizando os separadores no topo!"
        )
        box.pack_start(label, True, True, 0)
        return box

    @staticmethod
    def ui_introduction_tab():
        box = Gtk.Box()
        label = Gtk.Label("Este separador é uma introdução")
        box.pack_start(label, True, True, 0)
        return box

    @staticmethod
    def ui_usage_tab():
        box = Gtk.Box()
        label = Gtk.Label("Este é o separador da utilização")
        box.pack_start(label, True, True, 0)
        return box
