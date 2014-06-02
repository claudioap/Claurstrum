#!/bin/python3
from gi.repository import Gtk, Gio
import json


class MainWindow(Gtk.Window):

    def __init__(self):
        # Sets the window properties, and attaches the header bar.
        Gtk.Window.__init__(self, title="Claurstrum")
        self.set_default_size(1024, 600)

        header_bar = Gtk.HeaderBar()
        header_bar.props.show_close_button = True
        header_bar.props.title = "Claurstrum"
        header_bar.set_subtitle("The universal system setup tool")
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
            left_header_button_box = Gtk.Box()
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="document-open-symbolic")
            icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(icon)
            left_header_button_box.add(button)
            button = Gtk.Button("Reset")
            left_header_button_box.add(button)
            header_bar.pack_start(left_header_button_box)

            self.language_button = Gtk.Button("Language")
            self.language_button.connect('clicked', self.show_language_popover)
            header_bar.pack_end(self.language_button)
            Gtk.StyleContext.add_class(left_header_button_box.get_style_context(), "linked")

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

    @staticmethod
    def create_popover(element, content, title, subtitle, change):
        #Creates the popover for a given element with given content
        popover = Gtk.Popover.new(element)
        popover.set_relative_to(element)
        popover.set_modal(True)
        popover.set_position(Gtk.PositionType.BOTTOM)

        header_bar = Gtk.HeaderBar()
        if change:
            btn_r = Gtk.Button('Change')
            btn_r.set_can_focus(False)
            btn_r.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)
            header_bar.pack_end(btn_r)
        header_bar.set_title(title)
        if subtitle is not None:
            header_bar.set_subtitle(subtitle)

        content.set_hexpand(True)
        content.set_vexpand(True)
        content.set_halign(Gtk.Align.FILL)
        content.set_valign(Gtk.Align.FILL)

        grid = Gtk.Grid()
        grid.attach(header_bar, 0, 0, 1, 1)
        grid.attach(content, 0, 1, 1, 1)
        grid.set_border_width(15)
        popover.add(grid)
        grid.show_all()
        return popover

    def show_language_popover(self, *_):
        #Connects the language button to a popover
        content = Gtk.Box()
        content.set_size_request(600, 200)
        listbox = Gtk.ListBox()
        content.pack_start(listbox, True, True, 0)
        popover = self.create_popover(
            self.language_button, content,
            "Pick your language:",
            "Escolha a linguagem - Elige tu idioma - Choisissez votre langue - Wählen Sie Ihre Sprache",
            True
        )
        popover.show_all()
    
    def side_navigation_switch(self, listbox, row):
        # Whenever the current selected menu entry changes, 
        #  it changes the visible stack child
        if row is not None:
            self.stack.set_visible_child_name(row.get_child().get_text())

    @staticmethod
    def create_content_stack(menu):
        """This function a GTK.Notebook within a GTK.Stack. It fetches the
        known entries(menu, see below) from external python files, thus
        building the program interface from their information and methods.
        The menu variable, represents the whole menu tree from the
        JSON interface file. """
        stack = Gtk.Stack()
        categories = menu["name"]
        items = menu["items"]
        for x in range(len(items)):  # For every main entry
            try:  # Try to import the interface module referenced in the menu
                imported_ref = __import__(
                    'gtk_{mod}'.format(mod=menu["interface"][x])
                )
                ui_class = imported_ref.InterfaceModule()
            except ImportError:  # FIXME This should be more complete
                print("There was an error locating one module file!")
            else:
                tabbed_content = Gtk.Notebook()
                for y in range(len(items[x])):
                # For every minor entry of the current main entry
                    tabbed_content.append_page(
                        ui_class.ui[y], Gtk.Label(items[x][y]))
                tabbed_content.set_visible(True)
                stack.add_named(tabbed_content, categories[x])

        return stack