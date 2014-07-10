#!/bin/python3
import os.path
import subprocess
import re

from gi.repository import Gtk, Gdk, GLib


class InterfaceModule(Gtk.Box):
    def __init__(self, menu_entry):
        self.lbl_mem_usage = Gtk.Label("Memory Usage: N/A")
        self.lbl_cpu_usage = Gtk.Label("Processor Usage: N/A", xalign=1.0)
        self.lbl_nginx_result = Gtk.Label()
        self.start_button = Gtk.Button("Start")
        self.restart_button = Gtk.Button("Restart")
        self.stop_button = Gtk.Button("Stop")
        self.status_button = Gtk.Button("Status")
        self.notebook = None
        self.menu_entry = menu_entry
        self.encoded_pid = b''
        self.pid = None
        self.cpu = None
        self.mem = None
        self.interface = {'info': {}, 'setup': {}, 'ssl': {}, 'vhosts': {}}
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_info_tab(),
            self.ui_setup_tab(),
            self.ui_ssl_tab(),
            self.ui_vhost_tab()
        ]
        return ui

    def ui_info_tab(self):
        box = Gtk.Box(spacing=6)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(vbox, True, True, 1)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        vbox.pack_start(listbox, False, True, 0)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        hbox.set_border_width(5)

        nginx = Gtk.Label("Status:", xalign=1.0)
        hbox.pack_start(nginx, True, True, 0)
        hbox.pack_start(self.lbl_nginx_result, True, True, 15)

        hbox.pack_start(self.lbl_cpu_usage, True, True, 0)
        hbox.pack_start(self.lbl_mem_usage, False, True, 15)
        row.add(hbox)
        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_border_width(5)
        Gtk.StyleContext.add_class(hbox.get_style_context(), "linked")
        hbox.pack_start(self.start_button, True, True, 0)
        hbox.pack_start(self.restart_button, True, True, 0)
        hbox.pack_start(self.stop_button, True, True, 0)
        hbox.pack_start(self.status_button, True, True, 0)
        row.add(hbox)
        listbox.add(row)

        self.start_button.connect("clicked", self.start)
        self.start_button.set_sensitive(False)
        self.restart_button.connect("clicked", self.restart)
        self.restart_button.set_sensitive(False)
        self.stop_button.connect("clicked", self.stop)
        self.stop_button.set_sensitive(False)
        self.status_button.connect("clicked", self.status)
        self.status_button.set_sensitive(False)
        separator = Gtk.Separator()
        vbox.pack_start(separator, False, False, 0)

        self.refresh()
        GLib.timeout_add(5000, self.refresh)

        return box

    def ui_setup_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_bottom(0)
        box.set_margin_top(10)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        label = Gtk.Label("Top level host:")
        hbox.pack_start(label, False, True, 0)
        self.interface['setup']['host_switch'] = Gtk.Switch()
        hbox.pack_start(self.interface['setup']['host_switch'], False, True, 0)
        hbox.set_margin_left(20)
        hbox.set_margin_right(20)
        box.pack_start(hbox, False, True, 0)

        separator = Gtk.Separator()
        box.pack_start(separator, False, False, 0)

        grid = Gtk.Grid()
        grid.set_margin_left(20)
        grid.set_margin_right(20)
        grid.set_column_spacing(30)
        grid.set_row_spacing(1)

        #--------------- First Column ---------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Hostname:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['host'] = Gtk.Entry()
        hbox.pack_start(self.interface['setup']['host'], True, False, 0)
        grid.attach(hbox, 0, 0, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("IPV4:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['ipv4'] = Gtk.Entry()
        hbox.pack_start(self.interface['setup']['ipv4'], True, False, 0)
        grid.attach(hbox, 0, 1, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        self.interface['setup']['ipv6_on'] = Gtk.CheckButton(
            label="Enable IPV6")
        hbox.pack_start(
            self.interface['setup']['ipv6_on'], True, False, 0)
        grid.attach(hbox, 0, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("IPV6:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['ipv6'] = Gtk.Entry()
        hbox.pack_start(self.interface['setup']['ipv6'], True, False, 0)
        grid.attach(hbox, 0, 3, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Port:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['port'] = Gtk.Entry()
        hbox.pack_start(self.interface['setup']['port'], True, False, 0)
        grid.attach(hbox, 0, 4, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        self.interface['setup']['reverse_proxy'] = Gtk.CheckButton(
            label="Enable reverse Proxy:")
        label.set_margin_top(20)
        hbox.pack_start(
            self.interface['setup']['reverse_proxy'], True, False, 0)
        grid.attach(hbox, 0, 5, 1, 2)

        #--------------- Second Column ---------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        self.interface['setup']['document_root_label'] = Gtk.Label("Path:")
        hbox.pack_start(
            self.interface['setup']['document_root_label'], True, False, 0)
        label = Gtk.Label("/srv/http/")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['document_root'] = Gtk.FileChooserButton()
        hbox.pack_start(
            self.interface['setup']['document_root'], True, False, 0)
        grid.attach(hbox, 1, 0, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Log folder:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['log_folder_label'] = Gtk.Label("")
        hbox.pack_start(self.interface['setup']['log_folder_label'], True, False, 0)
        self.interface['setup']['log_folder'] = Gtk.FileChooserButton()
        hbox.pack_start(self.interface['setup']['log_folder'], True, False, 0)
        grid.attach(hbox, 1, 1, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Maximum connections:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['max_connections'] =\
            Gtk.SpinButton.new_with_range(1, 9999, 1)
        hbox.pack_start(self.interface['setup']['max_connections'], True, False, 0)
        grid.attach(hbox, 1, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label =\
            Gtk.Label("Number of workers:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['workers'] =\
            Gtk.SpinButton.new_with_range(1, 1000, 1)
        hbox.pack_start(self.interface['setup']['workers'], True, False, 0)
        grid.attach(hbox, 1, 3, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Keep alive time (seconds):")
        hbox.pack_start(label, True, False, 0)
        spin_button = Gtk.SpinButton.new_with_range(1, 1000, 1)
        hbox.pack_start(spin_button, True, False, 0)
        grid.attach(hbox, 1, 4, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(hbox.get_style_context(), "linked")
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['reverse_ip'] = Gtk.Entry()
        hbox.pack_start(self.interface['setup']['reverse_ip'], False, False, 0)
        self.interface['setup']['reverse_port'] = Gtk.Entry()
        self.interface['setup']['reverse_port'].set_width_chars(5)
        self.interface['setup']['reverse_port'].set_max_width_chars(5)
        hbox.pack_start(self.interface['setup']['reverse_port'], False, False, 0)
        ipv = Gtk.ComboBoxText()
        ipv.append("4", "IPV4")
        ipv.append("6", "IPV6")
        hbox.pack_end(ipv, False, False, 0)

        grid.attach(hbox, 1, 6, 1, 1)

        #--------------- Third Column ---------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['ssl_on'] = Gtk.CheckButton(label="Enable SSL")
        hbox.pack_start(self.interface['setup']['ssl_on'], True, False, 0)
        grid.attach(hbox, 2, 0, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['gzip_on'] =\
            Gtk.CheckButton(label="GZIP Compress")
        hbox.pack_start(self.interface['setup']['gzip_on'], True, False, 0)
        grid.attach(hbox, 2, 1, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_on'] =\
            Gtk.CheckButton(label="Enable PHP Support")
        hbox.pack_start(self.interface['setup']['php_on'], True, False, 0)
        grid.attach(hbox, 2, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_mdb_on'] =\
            Gtk.CheckButton(label="PHP - Enable MariaDB")
        hbox.pack_start(self.interface['setup']['php_mdb_on'], True, False, 0)
        grid.attach(hbox, 2, 3, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_sqlite_on'] =\
            Gtk.CheckButton(label="PHP - Enable SQLite")
        hbox.pack_start(self.interface['setup']['php_sqlite_on'], True, False, 0)
        grid.attach(hbox, 2, 4, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_myadmin_on'] =\
            Gtk.CheckButton(label="PHP - Install PHPMyAdmin")
        hbox.pack_start(
            self.interface['setup']['php_myadmin_on'], True, False, 0)
        grid.attach(hbox, 2, 5, 1, 1)

        box.pack_start(grid, True, True, 0)

        button = Gtk.Button("Apply")
        button.connect("clicked", self.apply_new_setup)
        box.pack_end(button, False, False, 0)

        return box

    @staticmethod
    def ui_ssl_tab():
        box = Gtk.Box()
        return box

    @staticmethod
    def ui_vhost_tab():
        box = Gtk.Box()
        return box

    def refresh(self, *_):
        if os.path.isfile("/usr/bin/nginx"):
            try:
                self.encoded_pid = subprocess.check_output(["pgrep nginx"], shell=True)
            except subprocess.CalledProcessError:
                self.lbl_nginx_result.set_text("Installed, not running")
                self.lbl_nginx_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=1.0, green=0.80, blue=0.0, alpha=1.0)
                )
                self.start_button.set_sensitive(True)
                self.stop_button.set_sensitive(False)
                self.status_button.set_sensitive(False)
                self.restart_button.set_sensitive(False)
            else:
                self.lbl_nginx_result.set_text("Running")
                self.lbl_nginx_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=0.0, green=0.8, blue=0.0, alpha=1.0)
                )
                self.pid = self.encoded_pid.decode("utf-8")
                self.pid = re.split('\n', self.pid)[0]
                info = subprocess.check_output(
                    ["ps -p " + self.pid + " -o %cpu,%mem"], shell=True
                )
                try:
                    info = info.decode("utf-8")
                    info = re.split('\n', info)[1]
                    info = re.split(' ', info)
                    self.cpu = info[1]
                    self.mem = info[3]
                except IndexError:
                    self.pid = None
                    self.encoded_pid = None
                    self.cpu = None
                    self.mem = None
                    self.lbl_cpu_usage.set_text("Processor Usage: N/A")
                    self.lbl_mem_usage.set_text("Memory Usage: N/A")
                else:
                    self.lbl_cpu_usage.set_text(
                        "Processor Usage: %s %%" % self.cpu
                    )
                    self.lbl_mem_usage.set_text(
                        "Memory Usage: %s %%" % self.mem
                    )
                self.start_button.set_sensitive(False)
                self.stop_button.set_sensitive(True)
                self.status_button.set_sensitive(True)
                self.restart_button.set_sensitive(True)
        else:
            self.lbl_nginx_result.set_text("Not installed")
            self.lbl_nginx_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=0.8, green=0.0, blue=0.0, alpha=1.0)
                )
            return False
        return True

    def start(self, *_):
        try:
            subprocess.check_output(["sudo systemctl start nginx"],shell=True)
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Success!")
            dialog.format_secondary_text("The Web Server was started.")
            dialog.run()
            self.refresh()
            dialog.destroy()
        except subprocess.CalledProcessError:
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Error:")
            dialog.format_secondary_text("There was an error. Find it out by yourself!")
            dialog.run()
            dialog.destroy()

    def restart(self, *_):
        try:
            subprocess.check_output(["sudo systemctl restart nginx"],shell=True)
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Success!")
            dialog.format_secondary_text("The Web Server was restarted.")
            dialog.run()
            dialog.destroy()
        except subprocess.CalledProcessError:
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Error:")
            dialog.format_secondary_text("There was an error. Find it out by yourself!")
            dialog.run()
            self.refresh()
            dialog.destroy()

    def stop(self, *_):
        try:
            subprocess.check_output(["sudo systemctl stop nginx"],shell=True)
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Success!")
            dialog.format_secondary_text("The Web Server was stopped.")
            dialog.run()
            dialog.destroy()
        except subprocess.CalledProcessError:
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Error:")
            dialog.format_secondary_text("There was an error. Find it out by yourself!")
            dialog.run()
            self.refresh()
            dialog.destroy()

    def status(self, *_):
        try:
            message = subprocess.check_output(["systemctl status nginx"],shell=True)
            message = message.decode("utf-8")
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Success!")
            dialog.format_secondary_text(message)
            dialog.run()
            dialog.destroy()
        except subprocess.CalledProcessError:
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Error:")
            dialog.format_secondary_text("The service seems not to be running!")
            dialog.run()
            self.refresh()
            dialog.destroy()

    def apply_new_setup(self, *_):
        pass
