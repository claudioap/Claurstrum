#!/bin/python3
import os
import re
import subprocess

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
        self.ui = self.build_ui()
        self.encoded_pid = b''
        self.pid = None
        self.cpu = None
        self.mem = None

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

    @staticmethod
    def ui_settings():
        box = Gtk.Box()
        return box

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