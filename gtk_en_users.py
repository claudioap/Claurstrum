#!/bin/python3
from gi.repository import Gtk
from textwrap import dedent


class InterfaceModule(Gtk.Box):
    def __init__(self, menu_entry):
        self.ui = self.build_ui()
        self.menu_entry = menu_entry
        self.notebook = None

    def build_ui(self):
        ui = [
            self.ui_users_tab()
        ]
        return ui

    def ui_users_tab(self):
        box = Gtk.Box()
        window_scroll = Gtk.ScrolledWindow()

        liststore = Gtk.ListStore(str, int, int, str, str, str)
        users_file = open("/etc/passwd", "r", encoding="utf-8").read()
        users_array = users_file.split("\n")
        users = []
        for x in users_array:
            users.append(x.split(":"))
        for user in users:
            if user == ['']:
                break
            liststore.append(
                [user[0], int(user[2]), int(user[3]), user[4], user[5], user[6]])

        treeview = Gtk.TreeView(model=liststore)

        column_renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Username", column_renderer, text=0)
        treeview.append_column(column)

        column_renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("UID", column_renderer, text=1)
        treeview.append_column(column)

        column_renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("GID", column_renderer, text=2)
        treeview.append_column(column)

        column_renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", column_renderer, text=3)
        treeview.append_column(column)

        column_renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Home", column_renderer, text=4)
        treeview.append_column(column)

        column_renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Shell", column_renderer, text=5)
        treeview.append_column(column)

        window_scroll.add(treeview)
        box.pack_start(window_scroll, True, True, 0)
        box.set_margin_left(1)
        return box

    def connect_self_to_nb(self):
        self.notebook.interface_module = self

    def open_config(self, file):
        pass