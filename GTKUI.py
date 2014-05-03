#!/bin/python3
from gi.repository import Gtk
import json


class MainWindow(Gtk.Window):

    def __init__(self):
        # Sets the window properties, and attaches the header bar.
        Gtk.Window.__init__(self, title="Claurstrum")
        self.set_default_size(1024, 600)

        header_bar = Gtk.HeaderBar()
        header_bar.props.show_close_button = True
        header_bar.props.title = "Claurstrum"
        self.set_titlebar(header_bar)
        
        # Tries to load the interface data from a JSON file,
        #  if fails shows an error
        try:
            json_interface_data = open(
                "interface.json", "r", encoding="utf-8")
            interface_data = json.load(json_interface_data)
        
        except ValueError:
            error = Gtk.Label(
                "There was an error loading a configuration file.")
            self.add(error)
        else:
            # Creates a two panel view, sidebar and content
            container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self.add(container)
            container.pack_start(
                self.create_side_navigation(
                    interface_data["menu"]["name"]), False, False, 0)

            self.stack = self.create_content_stack(interface_data["menu"])
            container.pack_start(self.stack, True, True, 0)

    def create_side_navigation(self, menu):
        """ This function picks each item, makes an entry in the ListBox,
        and returns the resulting widget
        The menu variable, represents the main menu names from the JSON 
        interface file."""
        side_navigation_list = Gtk.ListBox()
        side_navigation_list.set_size_request(160, 0)
        for x in range(len(menu)):
            label = Gtk.Label(menu[x])
            label.props.xalign = 0.0
            side_navigation_list.add(label)
        side_navigation_list.connect("row-selected", self.side_navigation_switch)
        return side_navigation_list
    
    def side_navigation_switch(self, listbox, row):
        # Whenever the current selected menu entry changes, 
        #  it changes the visible stack child
        if row is not None:
            self.stack.set_visible_child_name(row.get_child().get_text())

    def create_content_stack(self, menu):
        """This function makes a stack filled with a Gtk.Notebook for every
        main menu entry, and within them creates the sub-menus and interface
        content. The menu variable, represents the whole menu tree from the
        JSON interface file. """
        stack = Gtk.Stack()
        categories = menu["name"]
        items = menu["items"]
        for x in range(len(items)):
            tabbed_content = Gtk.Notebook()
            for y in range(len(items[x])):
                # Insert content into the notebook stacks
                test_button = Gtk.Button("I am a button!\nBut not for long!")
                tabbed_content.append_page(test_button, Gtk.Label(items[x][y]))
            tabbed_content.set_visible(True)
            stack.add_named(tabbed_content, categories[x])

        return stack