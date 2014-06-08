#!/bin/python3
from gi.repository import Gtk, Gio
import json


class MainWindow(Gtk.Window):

    def __init__(self):
        # Sets the window properties, and attaches the header bar.
        Gtk.Window.__init__(self, title="Claurstrum")
        self.set_size_request(1024, 600)
        self.set_resizable(False)

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
            self.interface_data = json.load(json_interface_data)
            self.language = 0
            self.new_language = None

        except ValueError:
            error = Gtk.Label(
                "There was an error loading a configuration file.")
            self.add(error)
        else:
            #These still do nothing
            left_header_button_box = Gtk.Box()
            button = Gtk.Button()
            icon = Gio.ThemedIcon(name="document-open-symbolic")
            icon = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
            button.add(icon)
            left_header_button_box.add(button)
            button = Gtk.Button("Reset")
            left_header_button_box.add(button)
            Gtk.StyleContext.add_class(
                left_header_button_box.get_style_context(), "linked"
            )
            header_bar.pack_start(left_header_button_box)
            #Language button.
            # Pops a language selection menu when clicked
            self.language_button = Gtk.Button("Language")
            self.language_button.connect(
                'clicked', self.show_language_popover
            )
            header_bar.pack_end(self.language_button)
            #Inits class variables which will be the main interface widgets
            self.interface = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self.stack = None
            self.add(self.interface)

            self.build_interface()

    def build_interface(self):
        # Creates a two panel view, sidebar and content
        self.interface.pack_start(
            self.create_side_navigation(
                self.interface_data["menu"][self.language]["name"])
            , False, False, 0
        )

        self.stack = self.create_content_stack(
            self.interface_data["menu"][self.language]
        )
        self.interface.pack_start(self.stack, True, True, 0)

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
        side_navigation_list.connect(
            "row-selected", self.side_navigation_changed
        )
        return side_navigation_list

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
                ui_class = imported_ref.InterfaceModule(x)
            except ImportError:  # FIXME This should be more complete
                print("There was an error locating one module file!")
            else:
                tabbed_content = Gtk.Notebook()
                ui_class.notebook = tabbed_content
                for y in range(len(items[x])):
                # For every minor entry of the current main entry
                    tabbed_content.append_page(
                        ui_class.ui[y], Gtk.Label(items[x][y]))
                tabbed_content.set_visible(True)
                stack.add_named(tabbed_content, categories[x])

        return stack

    @staticmethod
    def create_popover(element, content, title, subtitle, change):
        # Creates the popover for a given element with given content
        # It may, or may not have approval buttons
        popover = Gtk.Popover.new(element)
        popover.set_relative_to(element)
        popover.set_modal(True)
        popover.set_position(Gtk.PositionType.BOTTOM)

        header_bar = Gtk.HeaderBar()
        if change:
            change_button = Gtk.Button('Change')
            change_button.set_can_focus(False)
            change_button.get_style_context().add_class(
                Gtk.STYLE_CLASS_SUGGESTED_ACTION
            )
            header_bar.pack_end(change_button)
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
        if change:
            return [popover, change_button]
        return popover

    def show_language_popover(self, *_):
        #Builds a language selection GTK.Popover on top of the language button
        content = Gtk.Box()
        content.set_size_request(600, 200)
        language_list = Gtk.ListBox()
        for language in range(len(self.interface_data['menu'])):
            label = Gtk.Label(
                self.interface_data['menu'][language]['language']
            )
            language_list.add(label)
        language_list.connect("row-selected", self.new_language_value_change)
        content.pack_start(language_list, True, True, 0)
        popover = self.create_popover(
            self.language_button, content,
            "Pick your language:",
            'Escolha a linguagem - Elige tu idioma - '
            'Choisissez votre langue - Wählen Sie Ihre Sprache',
            True
        )

        popover_menu = popover[0]
        popover_menu.show_all()
        popover_button = popover[1]
        popover_button.connect("clicked", self.language_change_confirmation)

    def new_language_value_change(self, listbox, row):
        """
        Changes the "self.new_language" into the current selected language row
        inside the popover listbox
        :param row: Selected row
        """
        if row is not None:
            self.new_language = {
                "Index": row.get_index(), "Name": row.get_child().get_text()
            }

    def language_change_confirmation(self, *_):
        """
        Shows the confirmation dialog. If succeeded destroys the widgets,
        then recreates new ones in the new language.
        """
        if self.new_language["Index"] != self.language:
            dialog = Gtk.Dialog()
            dialog.set_title("Confirmation:")
            dialog.set_transient_for(self)
            dialog.set_modal(True)
            dialog.add_button(
                button_text="OK", response_id=Gtk.ResponseType.OK
            )
            dialog.add_button(
                button_text="Cancel", response_id=Gtk.ResponseType.CANCEL
            )
            dialog_content = dialog.get_content_area()
            dialog_content.add(
                Gtk.Label(
                    "You are going to change the language to " +
                    self.new_language['Name'],
                    xalign=0.1
                )
            )
            dialog_content.set_size_request(360, 100)
            dialog.show_all()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.language = self.new_language["Index"]
                self.new_language = None

                self.interface.remove(self.stack)
                self.remove(self.interface)
                self.interface = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL
                )
                self.build_interface()
                self.interface.show_all()
                self.add(self.interface)
            dialog.destroy()

    def side_navigation_changed(self, listbox, row):
        # Whenever the current selected menu entry changes,
        #  it changes the visible stack child
        if row is not None:
            self.stack.set_visible_child_name(row.get_child().get_text())
