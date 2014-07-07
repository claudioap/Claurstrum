#!/bin/python3
import os.path
import subprocess
import re

from gi.repository import Gtk, Gdk, GLib


class InterfaceModule(Gtk.Box):

    def __init__(self, menu_entry):
        self.ui = self.build_ui()
        self.encoded_pid
        self.pid
        self.cpu = None
        self.mem = None
        self.lbl_cpu_usage
        self.lbl_mem_usage
        self.not_installed

    def build_ui(self):
        ui = [
            self.ui_info_tab(),
            self.ui_standard_setup_tab(),
            self.ui_ssl_tab(),
            self.ui_vhost_tab()
        ]
        return ui

    def ui_info_tab(self):
        box = Gtk.Box(spacing=6)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        box.pack_start(listbox, True, True, 1)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)

        nginx = Gtk.Label("Status:", xalign=0.5)
        hbox.pack_start(nginx, True, True, 0)

        if os.path.isfile("/usr/bin/nginx"):
            try:
                self.encoded_pid = subprocess.check_output(["pgrep nginx"], shell=True)
            except subprocess.CalledProcessError:
                nginx_result = Gtk.Label("Installed, not running", xalign=0)
                nginx_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=0.95, green=0.95, blue=0.0, alpha=1.0)
                )
            else:
                nginx_result = Gtk.Label("Running")
                nginx_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=0.0, green=0.8, blue=0.0, alpha=1.0)
                )
                self.pid = self.encoded_pid.decode("utf-8")
                self.pid = re.split('\n', self.pid)[0]
                GLib.timeout_add(5000, self.refresh_stats)
            self.not_installed = False
        else:
            nginx_result = Gtk.Label("Not installed")
            nginx_result.override_color(
                    Gtk.StateFlags.NORMAL,
                    Gdk.RGBA(red=0.8, green=0.0, blue=0.0, alpha=1.0)
                )
            self.not_installed = True
        hbox.pack_start(nginx_result, True, True, 0)
        row.add(hbox)
        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.lbl_cpu_usage = Gtk.Label("Processor Usage: N/A")
        hbox.pack_start(self.lbl_cpu_usage, True, True, 0)
        self.lbl_mem_usage = Gtk.Label("Memory Usage: N/A")
        hbox.pack_start(self.lbl_mem_usage, True, True, 0)
        row.add(hbox)
        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        start_button = Gtk.Button("Start")
        hbox.pack_start(start_button, True, True, 0)
        restart_button = Gtk.Button("Restart")
        hbox.pack_start(restart_button, True, True, 0)
        stop_button = Gtk.Button("Stop")
        hbox.pack_start(stop_button, True, True, 0)
        status_button = Gtk.Button("Status")
        hbox.pack_start(status_button, True, True, 0)
        row.add(hbox)
        listbox.add(row)

        return box

    @staticmethod
    def ui_standard_setup_tab():
        box = Gtk.Box()
        label = Gtk.Label("This is the first steps tab")
        box.pack_start(label, True, True, 0)
        return box

    @staticmethod
    def ui_ssl_tab():
        box = Gtk.Box()
        label = Gtk.Label("This is the first steps tab")
        box.pack_start(label, True, True, 0)
        return box

    @staticmethod
    def ui_vhost_tab():
        box = Gtk.Box()
        label = Gtk.Label("This is the first steps tab")
        box.pack_start(label, True, True, 0)
        return box

    def refresh_stats(self):
        try:
            encoded_pid = subprocess.check_output(["pgrep nginx"], shell=True)
            if self.encoded_pid != encoded_pid:
                if encoded_pid.decode("utf-8") != '':
                    self.encoded_pid = encoded_pid
                    self.pid = re.split('\n', encoded_pid.decode("utf-8"))[0]
                else:
                    self.pid = None
                    self.encoded_pid = None
                    self.cpu = None
                    self.mem = None

            if self.pid:
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

        except subprocess.CalledProcessError:
            if self.not_installed:
                return False
            self.pid = None
            self.encoded_pid = None
            self.cpu = None
            self.mem = None

        return True