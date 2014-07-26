#!/bin/python3
import os
import re
import socket
import subprocess
import json

from gi.repository import Gtk, Gdk, GLib


class InterfaceModule(Gtk.Box):

    def __init__(self, menu_entry):
        self.lbl_mem_usage = Gtk.Label("Memory Usage: N/A")
        self.lbl_cpu_usage = Gtk.Label("Processor Usage: N/A", xalign=1.0)
        self.lbl_sshd_result = Gtk.Label()
        self.start_button = Gtk.Button("Start")
        self.restart_button = Gtk.Button("Restart")
        self.stop_button = Gtk.Button("Stop")
        self.status_button = Gtk.Button("Status")
        self.encoded_pid = b''
        self.pid = None
        self.cpu = None
        self.mem = None
        self.settings_interface = {'container': None, 'holder': None}
        self.config_file = None
        self.config = None
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_info_tab(),
            self.ui_settings()
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

        sshd = Gtk.Label("Status:", xalign=1.0)
        hbox.pack_start(sshd, True, True, 0)
        hbox.pack_start(self.lbl_sshd_result, True, True, 15)

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

    def ui_settings(self):
        self.settings_interface['container'] = Gtk.Box()
        if self.settings_interface['holder'] is not None:
            self.settings_interface['container'].remove(
                self.settings_interface['holder'])
        self.settings_interface['holder'] = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL)
        grid = Gtk.Grid()
        grid.set_margin_top(20)
        grid.set_margin_left(20)
        grid.set_margin_right(20)
        grid.set_column_spacing(50)
        grid.set_row_spacing(10)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("IPV4:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['ipv4'] = Gtk.Entry()
        hbox.pack_start(self.settings_interface['ipv4'], True, False, 0)
        grid.attach(hbox, 0, 0, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("IPV6:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['ipv6'] = Gtk.Entry()
        hbox.pack_start(self.settings_interface['ipv6'], True, False, 0)
        grid.attach(hbox, 1, 0, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Port:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['port'] = Gtk.Entry()
        self.settings_interface['port'].set_width_chars(5)
        self.settings_interface['port'].set_max_width_chars(5)
        hbox.pack_start(self.settings_interface['port'], True, False, 0)
        grid.attach(hbox, 2, 0, 1, 1)

        #----------------------------------------------------------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Login Timeout:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['timeout'] = Gtk.SpinButton.new_with_range(1, 100, 1)
        hbox.pack_start(self.settings_interface['timeout'], True, False, 0)
        grid.attach(hbox, 0, 1, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Max. Tries:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['tries'] = Gtk.SpinButton.new_with_range(0, 100, 1)
        hbox.pack_start(self.settings_interface['tries'], True, False, 0)
        grid.attach(hbox, 1, 1, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Sessions:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['sessions'] = Gtk.SpinButton.new_with_range(0, 10, 1)
        hbox.pack_start(self.settings_interface['sessions'], True, False, 0)
        grid.attach(hbox, 2, 1, 1, 1)

        #----------------------------------------------------------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Password auth:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['password'] = Gtk.Switch(active=True)
        hbox.pack_start(self.settings_interface['password'], True, False, 0)
        grid.attach(hbox, 0, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Host Auth:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['host_auth'] = Gtk.Switch()
        hbox.pack_start(self.settings_interface['host_auth'], True, False, 0)
        grid.attach(hbox, 1, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Root Login:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['root_login'] = Gtk.Switch()
        hbox.pack_start(self.settings_interface['root_login'], True, False, 0)
        grid.attach(hbox, 2, 2, 1, 1)

        #----------------------------------------------------------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("TCP Forward:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['tcp'] = Gtk.Switch()
        hbox.pack_start(self.settings_interface['tcp'], True, False, 0)
        grid.attach(hbox, 0, 3, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("X11 Forward:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['x11'] = Gtk.Switch()
        hbox.pack_start(self.settings_interface['x11'], True, False, 0)
        grid.attach(hbox, 1, 3, 1, 1)
        #----------------------------------------------------------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Message:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['message'] = Gtk.Entry()
        hbox.pack_start(self.settings_interface['message'], True, False, 0)
        grid.attach(hbox, 0, 4, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Log Location:")
        hbox.pack_start(label, True, False, 0)
        self.settings_interface['log'] = Gtk.FileChooserButton()
        hbox.pack_start(self.settings_interface['log'], True, False, 0)
        grid.attach(hbox, 2, 4, 1, 1)

        self.settings_interface['holder'].pack_start(grid, True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(hbox.get_style_context(), "linked")
        write_button = Gtk.Button(label="Write")
        apply_button = Gtk.Button(label="Apply written config")
        write_button.connect("clicked", self.write_config)
        apply_button.connect("clicked", self.apply_config)
        hbox.pack_start(write_button, True, True, 0)
        hbox.pack_start(apply_button, True, True, 0)
        self.settings_interface['holder'].pack_start(hbox, False, True, 0)

        self.settings_interface['container'].pack_start(
            self.settings_interface['holder'], True, True, 0)
        return self.settings_interface['container']

    def refresh(self, *_):
        if os.path.isfile("/usr/bin/sshd"):
            try:
                self.encoded_pid = subprocess.check_output(["pgrep sshd"], shell=True)
            except subprocess.CalledProcessError:
                self.lbl_sshd_result.set_text("Installed, not running")
                self.lbl_sshd_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=1.0, green=0.80, blue=0.0, alpha=1.0)
                )
                self.start_button.set_sensitive(True)
                self.stop_button.set_sensitive(False)
                self.status_button.set_sensitive(False)
                self.restart_button.set_sensitive(False)
            else:
                self.lbl_sshd_result.set_text("Running")
                self.lbl_sshd_result.override_color(
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
            self.lbl_sshd_result.set_text("Not installed")
            self.lbl_sshd_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=0.8, green=0.0, blue=0.0, alpha=1.0)
                )
            return False
        return True

    def start(self, *_):
        try:
            subprocess.check_output(["sudo systemctl start sshd"],shell=True)
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
            subprocess.check_output(["sudo systemctl restart sshd"],shell=True)
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
            subprocess.check_output(["sudo systemctl stop sshd"],shell=True)
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
            message = subprocess.check_output(["systemctl status sshd"],shell=True)
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

    def write_config(self, *_):
        valid = True
        ipv4 = self.settings_interface['ipv4'].get_text()
        ipv6 = self.settings_interface['ipv6'].get_text()
        port =self.settings_interface['port'].get_text()
        timeout = self.settings_interface['timeout'].get_value()
        tries = self.settings_interface['tries'].get_value()
        sessions = self.settings_interface['sessions'].get_value()
        password = self.settings_interface['password'].get_active()
        host_auth = self.settings_interface['host_auth'].get_active()
        root = self.settings_interface['root_login'].get_active()
        tcp = self.settings_interface['tcp'].get_active()
        x11 = self.settings_interface['x11'].get_active()
        message = self.settings_interface['message'].get_text()
        log_file = self.settings_interface['log'].get_filename()

        ips = []
        if self.valid_ipv4(ipv4):
            ips.append(ipv4)
        else:
            ipv4 = None

        if self.valid_ipv6(ipv6):
            ips.append(ipv6)
        else:
            ipv6 = None

        if ipv4 is None and ipv6 is None:
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Invalid IPs:")
            dialog.format_secondary_text(
                "There are no valid IPs configured")
            dialog.run()
            dialog.destroy()

        try:
            port = int(port)
        except ValueError:
            valid = False
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Invalid port:")
            dialog.format_secondary_text(
                "Invalid port field: Not a number.")
            dialog.run()
            dialog.destroy()
        else:
            if port > 65535 or port < 1:
                valid = False
                dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="Invalid port:")
                dialog.format_secondary_text(
                    "Invalid port number: Out of valid range")
                dialog.run()
                dialog.destroy()

        if log_file is None:
            valid = False
            dialog = Gtk.MessageDialog(transient_for=None,
                                   modal=True,
                                   destroy_with_parent=True,
                                   message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.CLOSE,
                                   text="Invalid port:")
            dialog.format_secondary_text(
                "No log file selected")
            dialog.run()
            dialog.destroy()

        if valid:
            self.config = {'ip': ips, 'port': port, 'root': root,
                      'password_auth': password, 'host_auth': host_auth,
                      'timeout': timeout, 'tries': tries, 'sessions': sessions,
                      'tcp': tcp, 'x11': x11, 'log': log_file,
                      'message': message}
            dialog = Gtk.FileChooserDialog(
                "Please make a config file", None,
                Gtk.FileChooserAction.SAVE,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
                 Gtk.ResponseType.OK))

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.config_file = dialog.get_filename()
            elif self.config_file is None:
                valid = False
            dialog.destroy()

        if valid:
            file = open(self.config_file, 'w', encoding="utf-8")
            file.write(json.dumps(self.config))

    def apply_config(self, *_):
        if self.config_file is not None:
            config_file = open(self.config_file, 'r', encoding="utf-8")
            config = json.load(config_file)
            if self.valid_config(config):
                self.gen_server_config(config)

        else:
            dialog = Gtk.MessageDialog(transient_for=None,
                                       modal=True,
                                       destroy_with_parent=True,
                                       message_type=Gtk.MessageType.INFO,
                                       buttons=Gtk.ButtonsType.CLOSE,
                                       text="No saved config:")
            dialog.format_secondary_text(
                "You need to write a config file before you can apply " +
                "its changes!")
            dialog.run()
            dialog.destroy()

    @staticmethod
    def valid_config(config):
        if 'ip' in config and 'port' in config and 'timeout' in config and\
            'sessions' in config and 'log' in config and 'password_auth' in\
            config and 'host_auth' in config and 'tries' in config and\
            'x11' in config and 'message' in config and 'tcp' in config and\
                'root' in config:
            for ip in config['ip']:
                if InterfaceModule.valid_ipv4(ip) ==\
                        InterfaceModule.valid_ipv6(ip):
                    return False

            if not (0 < config['port'] < 65536):
                return False

            return True
        else:
            return False

    def gen_server_config(self, config):
        pass

    def connect_self_to_nb(self):
        self.notebook.interface_module = self

    def open_config(self, file):
        print(file)

    @staticmethod
    def valid_ipv4(address):
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:
            return False
        return True

    @staticmethod
    def valid_ipv6(address):
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:
            return False
        return True