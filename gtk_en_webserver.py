#!/bin/python3
import os.path
import subprocess
import re
import json
import socket

from gi.repository import Gtk, Gdk, GLib
from jinja2 import FileSystemLoader, Environment


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
        self.loaded_config = None
        self.interface = {
            'info': {}, 'setup': {}, 'ssl': {}, 'vhosts_container': None,
            'vhosts_list': None, 'vhosts': []}
        self.ui = self.build_ui()

    def build_ui(self):
        ui = [
            self.ui_info_tab(),
            self.ui_setup_tab(),
            self.ui_ssl_tab(),
            self.ui_vhost_tab()
        ]
        path = "./webserver.claur"
        if os.path.exists(path):
            self.open_config(path)
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
        self.interface['setup']['host_switch'] = Gtk.Switch(active=True)
        self.interface['setup']['host_switch'].connect(
            "notify::active", self.enable_host)
        hbox.pack_start(self.interface['setup']['host_switch'], False, True, 0)
        hbox.set_margin_left(20)
        hbox.set_margin_right(20)
        box.pack_start(hbox, False, True, 0)

        separator = Gtk.Separator()
        box.pack_start(separator, False, False, 0)

        grid = Gtk.Grid()
        grid.set_margin_left(20)
        grid.set_margin_right(20)
        grid.set_column_spacing(20)
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
        self.interface['setup']['ipv6_on'].connect(
            "notify::active", self.activate_ipv6)
        hbox.pack_start(
            self.interface['setup']['ipv6_on'], True, False, 0)
        grid.attach(hbox, 0, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("IPV6:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['ipv6'] = Gtk.Entry(sensitive=False)
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
        self.interface['setup']['reverse_proxy'].connect(
            "notify::active", self.activate_reverse_proxy)
        hbox.pack_start(
            self.interface['setup']['reverse_proxy'], True, False, 0)
        grid.attach(hbox, 0, 5, 1, 2)

        #--------------- Second Column ---------------------
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.END)
        label = Gtk.Label("Path:")
        hbox.pack_start(label, True, False, 0)
        self.interface['setup']['document_root_label'] = Gtk.Label("")
        hbox.pack_start(
            self.interface['setup']['document_root_label'], True, False, 0)
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
        self.interface['setup']['keep_alive'] =\
            Gtk.SpinButton.new_with_range(1, 1000, 1)
        hbox.pack_start(self.interface['setup']['keep_alive'], True, False, 0)
        grid.attach(hbox, 1, 4, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(hbox.get_style_context(), "linked")
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['reverse_ip'] = Gtk.Entry(sensitive=False)
        hbox.pack_start(self.interface['setup']['reverse_ip'], False, False, 0)
        self.interface['setup']['reverse_port'] = Gtk.Entry(sensitive=False)
        self.interface['setup']['reverse_port'].set_width_chars(5)
        self.interface['setup']['reverse_port'].set_max_width_chars(5)
        hbox.pack_start(
            self.interface['setup']['reverse_port'], False, False, 0)
        self.interface['setup']['reverse_ipv'] =\
            Gtk.ComboBoxText(sensitive=False)
        self.interface['setup']['reverse_ipv'].append("4", "IPV4")
        self.interface['setup']['reverse_ipv'].append("6", "IPV6")
        hbox.pack_end(self.interface['setup']['reverse_ipv'], False, False, 0)

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
        self.interface['setup']['php_on'].connect(
            "notify::active", self.activate_php)
        hbox.pack_start(self.interface['setup']['php_on'], True, False, 0)
        grid.attach(hbox, 2, 2, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_mdb_on'] =\
            Gtk.CheckButton(label="PHP - Enable MariaDB", sensitive=False)
        self.interface['setup']['php_mdb_on'].connect(
            "notify::active", self.activate_php)
        hbox.pack_start(self.interface['setup']['php_mdb_on'], True, False, 0)
        grid.attach(hbox, 2, 3, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_sqlite_on'] =\
            Gtk.CheckButton(label="PHP - Enable SQLite", sensitive=False)
        hbox.pack_start(
            self.interface['setup']['php_sqlite_on'], True, False, 0)
        grid.attach(hbox, 2, 4, 1, 1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.set_halign(Gtk.Align.START)
        self.interface['setup']['php_myadmin_on'] =\
            Gtk.CheckButton(label="PHP - Install PHPMyAdmin", sensitive=False)
        hbox.pack_start(
            self.interface['setup']['php_myadmin_on'], True, False, 0)
        grid.attach(hbox, 2, 5, 1, 1)

        box.pack_start(grid, True, True, 0)

        button = Gtk.Button("Apply")
        button.connect("clicked", self.apply_setup)
        box.pack_end(button, False, False, 0)

        return box

    @staticmethod
    def ui_ssl_tab():
        box = Gtk.Box()
        return box

    def ui_vhost_tab(self):
        self.interface['vhosts_container'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        return self.interface['vhosts_container']

    def vhosts_load(self):
        if self.interface['vhosts_list'] is not None:
            self.interface['vhosts_container'].remove(
                self.interface['vhosts_list'])

        self.interface['vhosts_list'] = Gtk.ListBox()
        self.interface['vhosts_list'].set_selection_mode(
            Gtk.SelectionMode.NONE)
        count = 0
        hosts = self.loaded_config[0]
        for host in hosts:
            print(host)
            row = Gtk.ListBoxRow()
            expander = Gtk.Expander.new_with_mnemonic(host[0]['hostname'])
            row.add(expander)
            grid = Gtk.Grid()
            grid.set_margin_left(20)
            grid.set_margin_right(20)
            grid.set_column_spacing(20)
            grid.set_row_spacing(1)
            #--------------- First Column ---------------------
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            label = Gtk.Label("Hostname:")
            hbox.pack_start(label, True, False, 0)
            self.interface['vhosts'].append({})
            self.interface['vhosts'][count]['hostname'] = Gtk.Entry()
            self.interface['vhosts'][count]['hostname'].\
                set_text(host[0]['hostname'])
            hbox.pack_start(
                self.interface['vhosts'][count]['hostname'], True, False, 0)
            grid.attach(hbox, 0, 0, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            label = Gtk.Label("IPV4:")
            hbox.pack_start(label, True, False, 0)
            self.interface['vhosts'][count]['ip'] = Gtk.Entry()
            if not host[4]:
                self.interface['vhosts'][count]['ip'].set_text("N/A")
            else:
                self.interface['vhosts'][count]['ip'].set_text(
                    host[0]["ip"]
                )
            hbox.pack_start(
                self.interface['vhosts'][count]['ip'], True, False, 0)
            grid.attach(hbox, 0, 1, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            label = Gtk.Label("IPV6:")
            hbox.pack_start(label, True, False, 0)
            self.interface['vhosts'][count]['ipv6'] = Gtk.Entry()
            if not host[5]:
                self.interface['vhosts'][count]['ipv6'].set_text("N/A")
            else:
                self.interface['vhosts'][count]['ipv6'].set_text(
                    host[0]["ipv6"]
                )
            hbox.pack_start(
                self.interface['vhosts'][count]['ipv6'], True, False, 0)
            grid.attach(hbox, 0, 2, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            label = Gtk.Label("Port:")
            hbox.pack_start(label, True, False, 0)
            self.interface['vhosts'][count]['port'] = Gtk.Entry()
            self.interface['vhosts'][count]['port'].set_text(
                    str(host[0]["port"]))
            hbox.pack_start(
                self.interface['vhosts'][count]['port'], True, False, 0)
            grid.attach(hbox, 0, 3, 1, 1)

            #--------------- Second Column ---------------------
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            label = Gtk.Label("Path:")
            hbox.pack_start(label, True, False, 0)
            if host[2]:
                self.interface['vhosts'][count]['document_root_label'] =\
                    Gtk.Label("N/A")
            else:
                self.interface['vhosts'][count]['document_root_label'] =\
                    Gtk.Label(host[0]['root'])
            hbox.pack_start(
                self.interface['vhosts'][count]['document_root_label'],
                True, False, 0)
            self.interface['vhosts'][count]['document_root'] =\
                Gtk.FileChooserButton()
            hbox.pack_start(
                self.interface['vhosts'][count]['document_root'],
                True, False, 0)
            grid.attach(hbox, 1, 0, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            label = Gtk.Label("Log folder:")
            hbox.pack_start(label, True, False, 0)
            self.interface['vhosts'][count]['log_folder_label'] = Gtk.Label(
                host[0]['logs'])

            hbox.pack_start(self.interface['vhosts'][count]['log_folder_label']
                ,True ,False ,0)
            self.interface['vhosts'][count]['log_folder'] =\
                Gtk.FileChooserButton()
            hbox.pack_start(
                self.interface['vhosts'][count]['log_folder'], True, False, 0)
            grid.attach(hbox, 1, 1, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.END)
            self.interface['vhosts'][count]['reverse_proxy'] = Gtk.CheckButton(
                label="Enable reverse Proxy:")
            if host[2]:
                self.interface['vhosts'][count]['reverse_proxy'].\
                    set_active(True)
            self.interface['vhosts'][count]['reverse_proxy'].set_margin_top(20)
            hbox.pack_start(
                self.interface['vhosts'][count]['reverse_proxy'],
                True, False, 0)
            grid.attach(hbox, 1, 2, 1, 2)

            #--------------- Third Column ---------------------
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.START)
            self.interface['vhosts'][count]['ssl_on'] =\
                Gtk.CheckButton(label="Enable SSL")
            if host[1]:
                self.interface['vhosts'][count]['ssl_on'].set_active(True)
            hbox.pack_start(
                self.interface['vhosts'][count]['ssl_on'], True, False, 0)
            grid.attach(hbox, 2, 0, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            label = Gtk.Label("SSL Profile:")
            hbox.pack_start(label, False, False, 0)
            self.interface['vhosts'][count]['ssl_profile'] =\
                Gtk.ComboBoxText()
            self.interface['vhosts'][count]['ssl_profile'].\
                append("fixme", "SSL_PROFILE")
            hbox.pack_end(
                self.interface['vhosts'][count]['ssl_profile'],
                False, False, 0)
            grid.attach(hbox, 2, 1, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            hbox.set_halign(Gtk.Align.START)
            self.interface['vhosts'][count]['php_on'] =\
                Gtk.CheckButton(label="Enable PHP Support")
            if host[3]:
                self.interface['vhosts'][count]['php_on'].set_active(True)
            hbox.pack_start(
                self.interface['vhosts'][count]['php_on'], True, False, 0)
            grid.attach(hbox, 2, 2, 1, 1)

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            Gtk.StyleContext.add_class(hbox.get_style_context(), "linked")
            hbox.set_halign(Gtk.Align.START)
            self.interface['vhosts'][count]['reverse_proxy_ip'] =\
                Gtk.Entry()
            if host[2]:
                self.interface['vhosts'][count]['reverse_proxy_ip'].\
                    set_text(host[0]['reverse_proxy_ip'])
            hbox.pack_start(
                self.interface['vhosts'][count]['reverse_proxy_ip'],
                False, False, 0)
            self.interface['vhosts'][count]['reverse_proxy_port'] =\
                Gtk.Entry()
            if host[2]:
                self.interface['vhosts'][count]['reverse_proxy_port'].\
                    set_text(str(host[0]['reverse_proxy_port']))
            hbox.pack_start(
                self.interface['vhosts'][count]['reverse_proxy_port'],
                False, False, 0)

            self.interface['vhosts'][count]['reverse_proxy_port'].\
                set_width_chars(5)
            self.interface['vhosts'][count]['reverse_proxy_port'].\
                set_max_width_chars(5)
            self.interface['vhosts'][count]['reverse_proxy_ipv'] =\
                Gtk.ComboBoxText()
            self.interface['vhosts'][count]['reverse_proxy_ipv'].\
                append("4", "IPV4")
            self.interface['vhosts'][count]['reverse_proxy_ipv'].\
                append("6", "IPV6")
            hbox.pack_end(
                self.interface['vhosts'][count]['reverse_proxy_ipv'],
                False, False, 0)
            grid.attach(hbox, 2, 3, 1, 1)
            expander.add(grid)
            self.interface['vhosts_list'].add(row)
            for item in self.interface['vhosts'][count].values():
                item.row_count = count
            count += 1;
        self.interface['vhosts_list'].set_margin_left(1)
        self.interface['vhosts_container'].\
            pack_start(self.interface['vhosts_list'], True, True, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(hbox.get_style_context(), "linked")
        write_button = Gtk.Button(label="Write")
        apply_button = Gtk.Button(label="Apply written config")
        hbox.pack_start(write_button, True, True, 0)
        hbox.pack_start(apply_button, True, True, 0)
        self.interface['vhosts_container'].pack_start(hbox, False, True, 0)

        self.interface['vhosts_container'].show_all()

    def refresh(self, *_):
        if os.path.isfile("/usr/bin/nginx"):
            try:
                self.encoded_pid = subprocess.check_output(
                    ["pgrep nginx"], shell=True)
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

    def enable_host(self, widget, *_):
        if widget.get_active():
            self.enable_setup_widgets()
        else:
            self.disable_setup_widgets()

    def enable_setup_widgets(self):
        self.interface['setup']['host'].set_sensitive(True)
        self.interface['setup']['ipv4'].set_sensitive(True)
        self.interface['setup']['ipv6_on'].set_sensitive(True)
        self.interface['setup']['port'].set_sensitive(True)
        self.interface['setup']['reverse_proxy'].set_sensitive(True)
        self.interface['setup']['document_root_label'].set_sensitive(True)
        self.interface['setup']['document_root'].set_sensitive(True)
        self.interface['setup']['log_folder_label'].set_sensitive(True)
        self.interface['setup']['log_folder'].set_sensitive(True)
        self.interface['setup']['max_connections'].set_sensitive(True)
        self.interface['setup']['workers'].set_sensitive(True)
        self.interface['setup']['keep_alive'].set_sensitive(True)
        self.interface['setup']['ssl_on'].set_sensitive(True)
        self.interface['setup']['gzip_on'].set_sensitive(True)
        self.interface['setup']['php_on'].set_sensitive(True)
        self.activate_ipv6()
        self.activate_php()
        self.activate_reverse_proxy()

    def disable_setup_widgets(self):
        self.interface['setup']['host'].set_sensitive(False)
        self.interface['setup']['ipv4'].set_sensitive(False)
        self.interface['setup']['ipv6_on'].set_sensitive(False)
        self.interface['setup']['ipv6'].set_sensitive(False)
        self.interface['setup']['port'].set_sensitive(False)
        self.interface['setup']['reverse_proxy'].set_sensitive(False)
        self.interface['setup']['document_root_label'].set_sensitive(False)
        self.interface['setup']['document_root'].set_sensitive(False)
        self.interface['setup']['reverse_ip'].set_sensitive(False)
        self.interface['setup']['reverse_port'].set_sensitive(False)
        self.interface['setup']['reverse_ipv'].set_sensitive(False)
        self.interface['setup']['ssl_on'].set_sensitive(False)
        self.interface['setup']['php_on'].set_sensitive(False)
        self.interface['setup']['php_mdb_on'].set_sensitive(False)
        self.interface['setup']['php_sqlite_on'].set_sensitive(False)
        self.interface['setup']['php_myadmin_on'].set_sensitive(False)

    def activate_ipv6(self, *_):
        activated = self.interface['setup']['ipv6_on'].get_active()
        if activated:
            self.interface['setup']['ipv6'].set_sensitive(True)
        else:
            self.interface['setup']['ipv6'].set_sensitive(False)

    def activate_php(self, *_):
        activated = self.interface['setup']['php_on'].get_active()
        if activated:
            self.interface['setup']['php_mdb_on'].set_sensitive(True)
            self.interface['setup']['php_sqlite_on'].set_sensitive(True)
            if self.interface['setup']['php_mdb_on'].get_active():
                self.interface['setup']['php_myadmin_on'].set_sensitive(True)
            else:
                self.interface['setup']['php_myadmin_on'].set_sensitive(False)

        else:
            self.interface['setup']['php_mdb_on'].set_sensitive(False)
            self.interface['setup']['php_sqlite_on'].set_sensitive(False)
            self.interface['setup']['php_myadmin_on'].set_sensitive(False)

    def activate_reverse_proxy(self, *_):
        activated = self.interface['setup']['reverse_proxy'].get_active()
        if activated:
            self.interface['setup']['reverse_ip'].set_sensitive(True)
            self.interface['setup']['reverse_port'].set_sensitive(True)
            self.interface['setup']['reverse_ipv'].set_sensitive(True)
            self.interface['setup']['document_root_label'].set_sensitive(False)
            self.interface['setup']['document_root'].set_sensitive(False)
            self.interface['setup']['php_on'].set_sensitive(False)
            self.interface['setup']['php_mdb_on'].set_sensitive(False)
            self.interface['setup']['php_sqlite_on'].set_sensitive(False)
            self.interface['setup']['php_myadmin_on'].set_sensitive(False)
        else:
            self.interface['setup']['reverse_ip'].set_sensitive(False)
            self.interface['setup']['reverse_port'].set_sensitive(False)
            self.interface['setup']['reverse_ipv'].set_sensitive(False)
            self.interface['setup']['document_root_label'].set_sensitive(True)
            self.interface['setup']['document_root'].set_sensitive(True)
            self.interface['setup']['php_on'].set_sensitive(True)

    def load_config(self, config):#FIXME Valid Server/Main
        main = config['Main']
        hosts = config['VHosts']
        valid_hosts = []
        valid_ssl_profiles = []
        ssl = config['SSL']
        if 'connections' in main and 'processes' in main and\
                'alive_time' in main and 'gzip' in main:
            valid_server = True
            if 'on' in main and main['on'] is True and 'hostname' in main and\
                    'ip' in main and 'port' in main and 'logs' in main:
                valid_main = True
                if self.valid_ipv4(main['ip']):
                    valid_ipv4 = True
                else:
                    valid_ipv4 = False
                if 'ipv6' in main and self.valid_ipv6(main['ipv6']):
                    valid_ipv6 = True
                else:
                    valid_ipv6 = False
            else:
                valid_main = False
        else:
            valid_server = False
        if 'ssl_profile' in main and main['ssl_profile'] is not None:
            valid_ssl = True
        else:
            valid_ssl = False
        if 'reverse_proxy' in main and 'reverse_proxy_ip' in main and\
                'reverse_proxy_port' in main and 'reverse_proxy_ipv' in main:
            valid_reverse = True
        else:
            valid_reverse = False
        if 'root' in main and os.path.exists(main['root']):
            valid_root = True
        else:
            valid_root = False
        if (valid_reverse or main['reverse_proxy'] is True) and valid_root and\
            'php' in main and main['php'] is True and 'php_mdb' in main and\
            'php_sqlite' in main and (main['php_mdb'] is True == (
                'php_myadmin' in main and main['php_myadmin'] is True)):
            valid_php = True
        else:
            valid_php = False
        #--------------------- VHosts ------------------------------------------
        for host in hosts:
            if 'hostname' in host and 'port' in host and 'logs' in host:
                valid_host = True
                if 'ip' in main and self.valid_ipv4(host['ip']):
                    valid_ipv4 = True
                else:
                    valid_ipv4 = False
                if 'ipv6' in main and self.valid_ipv6(host['ipv6']):
                    valid_ipv6 = True
                else:
                    valid_ipv6 = False
                if not (valid_ipv4 or valid_ipv6):
                    valid_host = False
            else:
                valid_host = False

            if valid_host:
                if 'ssl_profile' in host and main['ssl_profile'] is not None:
                    valid_ssl = True
                else:
                    valid_ssl = False
                if 'reverse_proxy' in host and host['reverse_proxy'] is True\
                    and 'reverse_proxy_ip' in host and 'reverse_proxy_port'\
                        in main and 'reverse_proxy_ipv' in host:
                    valid_reverse = True
                    if host['reverse_proxy_ipv'] == "4":
                        if not self.valid_ipv4(host['reverse_proxy_ip']):
                            valid_reverse = False
                    elif host['reverse_proxy_ipv'] == "6":
                        if not self.valid_ipv6(host['reverse_proxy_ip']):
                            valid_reverse = False
                    else:
                        valid_reverse = False
                else:
                    valid_reverse = False
                if 'root' in host and os.path.exists(host['root']):
                    #if valid_reverse: FIXME
                    #    valid_host = False
                    pass
                else:
                    valid_host = False

                if not valid_reverse and 'php' in host and host['php'] is True:
                    valid_php = True
                else:
                    valid_php = False
            if valid_host:
                valid_hosts.append([host, valid_ssl, valid_reverse, valid_php,
                                    valid_ipv4, valid_ipv6])
        #------------------------ SSL ------------------------------------------
        for profile in ssl:
            if 'profile' in profile and 'cert' in profile and 'key' in profile:
                valid_profile = True
                if profile['profile'] is None or profile['profile'] == '':
                    valid_profile = False
                if not os.path.exists(profile['cert']):
                    valid_profile = False
                if not os.path.exists(profile['key']):
                    valid_profile = False
                if valid_profile:
                    valid_ssl_profiles.append(profile)
        #------------------- Relate SSL to Hosts -------------------------------
        count = 0
        for host in valid_hosts:
            if host[1] is True:
                host_cert = host[0]['ssl_profile']
                match = False
                for profile in valid_ssl_profiles:
                    if profile["Profile"] == host_cert:
                        match = True
                if match:
                    valid_hosts.pop(count)
                    count -= 1
            count += 1
        self.loaded_config = [valid_hosts, valid_ssl_profiles]
        self.vhosts_load();

    def apply_setup(self, *_):
        pass

    def gen_config(self, config):
        pass

    def connect_self_to_nb(self):
        self.notebook.interface_module = self

    def open_config(self, file):
        try:
            config_file = open(file, "r", encoding="utf-8")
            config = json.load(config_file)
        except ValueError:
            print("Invalid configuration file")
        else:
            if 'Main' not in config or\
                    'VHosts' not in config or\
                    'SSL' not in config:
                print("Invalid configuration file")
            else:
                self.load_config(config)

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

