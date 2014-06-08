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
            self.ui_welcome_tab(),
            self.ui_navigation_tab(),
            self.ui_further_tab()
        ]
        return ui

    def ui_welcome_tab(self):
        box = Gtk.Box()
        label = Gtk.Label(
            dedent("""
            Hi. The program welcomes you!
            \tIf you already know how to use it, then you're free to go!
            \t\tOtherwise this section will serve as an introduction to let you know how to use it.
            \t\tTo begin with, try to navigate using the tabs on top of this message. Click in the next one!
            \t\tThis category has as well buttons on the sides to help you navigate, you can use them!
            """),
            yalign=0,
            xalign=0,
            wrap=True
        )
        label.set_padding(20, 0)
        box.pack_start(label, True, True, 0)
        button = Gtk.Button("Continue")
        button.connect("clicked", self.next_page)
        box.pack_start(button, True, True, 0)
        return box

    def ui_navigation_tab(self):
        box = Gtk.Box()
        button = Gtk.Button("Previous")
        button.connect("clicked", self.prev_page)
        box.pack_start(button, True, True, 0)
        label = Gtk.Label(
            dedent("""
            Great! You managed to reach the second page of this category! :D
            \tThe tabs on the left of this rectangle are the categories (or modules).
            \tEach category has several pages, which you can check on top of the rectangle.
            \tRight now you are navigating the "Introduction"(check left) category.
            \tThis rectangle is a page, you're in the "Navigation"(check top) page.
            """),
            yalign=0,
            xalign=0,
            wrap=True
        )
        label.set_padding(20, 0)
        box.pack_start(label, True, True, 0)
        button = Gtk.Button("Continue")
        button.connect("clicked", self.next_page)
        box.pack_start(button, True, True, 0)
        return box

    def ui_further_tab(self):
        box = Gtk.Box()
        button = Gtk.Button(" Previous ")
        button.connect("clicked", self.prev_page)
        box.pack_start(button, False, True, 0)
        label = Gtk.Label(
            dedent("""
            If you are not comfortable reading English, you may click the "Language" button
            \t(title bar, left of the close button), and switch to another one.
            The categories are dependent on the language support, so a certain language may or
            \tmay not have certain features.
            This information will be continued as the program is developed...
            """),
            yalign=0,
            xalign=0,
            wrap=True
        )
        label.set_padding(20, 0)
        box.pack_start(label, True, True, 0)
        return box

    def prev_page(self, *_):
        self.notebook.prev_page()

    def next_page(self, *_):
        self.notebook.next_page()