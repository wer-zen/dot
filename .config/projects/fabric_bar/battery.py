import subprocess
import json
import logging
import time
from gi.repository import GLib
from fabric.utils.helpers import get_relative_path, monitor_file

import psutil
from fabric import Application
from fabric.core.fabricator import Fabricator
from fabric.widgets.box import Box
from fabric.widgets.button import Button
from fabric.widgets.circularprogressbar import CircularProgressBar
from fabric.widgets.eventbox import EventBox
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.revealer import Revealer
from fabric.utils.helpers import invoke_repeater
from fabric.widgets.scale import Scale

import icons
import data



class MetricsProvider:
    """
    Class responsible for obtaining centralized CPU, memory, disk usage, and battery metrics.
    It updates periodically so that all widgets querying it display the same values.
    """
    def __init__(self):


        self.bat_percent = 0.0
        self.bat_charging = None
        # Updates every 1 second (1000 milliseconds)
        GLib.timeout_add_seconds(1, self._update)

    def _update(self):


        battery = psutil.sensors_battery()
        if battery is None:
            self.bat_percent = 0.0
            self.bat_charging = None
        else:
            self.bat_percent = battery.percent
            self.bat_charging = battery.power_plugged

        return True  # keep the timeout


    def get_battery(self):
        return (self.bat_percent, self.bat_charging)



shared_provider = MetricsProvider()


class Battery(Button):
    def __init__(self, **kwargs):
        super().__init__(name="metrics-small", **kwargs)

        # Create the main box for metrics widgets
        main_box = Box(
            name="metrics-small",
            layer="top",
            anchor="top left right",
            spacing=0,
            orientation="h",
            visible=True,
            all_visible=True,
            style="background: transparent; padding: 10px;sucqs"
        )



        # ------------------ Battery ------------------
        self.bat_icon = Label(name="metrics-icon", markup=icons.battery)
        self.bat_circle = CircularProgressBar(
            name="metrics-circle",
            value=0,
            size=28,
            line_width=2,
            start_angle=150,
            end_angle=390,
            style_classes="bat",
            child=self.bat_icon,
        )
        self.bat_level = Label(name="metrics-level", style_classes="bat", label="100%")
        self.bat_revealer = Revealer(
            name="metrics-bat-revealer",
            transition_duration=250,
            transition_type="slide-left",
            child=self.bat_level,
            child_revealed=False,
        )
        self.bat_box = Box(
            name="metrics-bat-box",
            orientation="h",
            spacing=0,
            children=[self.bat_circle, self.bat_revealer],
        )

        # Add the battery widget to the main container
        main_box.add(self.bat_box)

        # Set the main box as the button's child
        self.add(main_box)

        # Connect events directly to the button
        self.connect("enter-notify-event", self.on_mouse_enter)
        self.connect("leave-notify-event", self.on_mouse_leave)

        # Actualización de la batería cada segundo
        self.batt_fabricator = Fabricator(
            poll_from=lambda v: shared_provider.get_battery(),
            on_changed=lambda f, v: self.update_battery,
            interval=1000,
            stream=False,
            default_value=0
        )
        self.batt_fabricator.changed.connect(self.update_battery)
        GLib.idle_add(self.update_battery, None, shared_provider.get_battery())

        # Estado inicial de los revealers y variables para la gestión del hover
        self.hide_timer = None
        self.hover_counter = 0



    def _format_percentage(self, value: int) -> str:
        """Formato natural del porcentaje sin forzar ancho fijo."""
        return f"{value}%"

    def on_mouse_enter(self, widget, event):
        if not data.VERTICAL:
            self.hover_counter += 1
            if self.hide_timer is not None:
                GLib.source_remove(self.hide_timer)
                self.hide_timer = None
            # Revelar niveles en hover para todas las métricas
            self.bat_revealer.set_reveal_child(True)
            return False

    def on_mouse_leave(self, widget, event):
        if not data.VERTICAL:
            if self.hover_counter > 0:
                self.hover_counter -= 1
            if self.hover_counter == 0:
                if self.hide_timer is not None:
                    GLib.source_remove(self.hide_timer)
                self.hide_timer = GLib.timeout_add(500, self.hide_revealer)
            return False

    def hide_revealer(self):
        if not data.VERTICAL:
            self.bat_revealer.set_reveal_child(False)
            self.hide_timer = None
            return False

    def update_battery(self, sender, battery_data):
        value, charging = battery_data
        if value == 0:
            self.set_visible(False)
        else:
            self.set_visible(True)
            self.bat_circle.set_value(value / 100)
        percentage = int(value)
        self.bat_level.set_label(self._format_percentage(percentage))

        # Apply alert styling if battery is low, regardless of charging status
        if percentage <= 15:
            self.bat_icon.add_style_class("alert")
            self.bat_circle.add_style_class("alert")
        else:
            self.bat_icon.remove_style_class("alert")
            self.bat_circle.remove_style_class("alert")

        # Choose the icon based on charging state first, then battery level
        if percentage == 100:
            self.bat_icon.set_markup(icons.battery)
            charging_status = f"{icons.bat_full} Fully Charged"
        elif charging == True:
            self.bat_icon.set_markup(icons.charging)
            charging_status = f"{icons.bat_charging} Charging"
        elif percentage <= 15 and charging == False:
            self.bat_icon.set_markup(icons.alert)
            charging_status = f"{icons.bat_low} Low Battery"
        elif charging == False:
            self.bat_icon.set_markup(icons.discharging)
            charging_status = f"{icons.bat_discharging} Discharging"
        else:
            self.bat_icon.set_markup(icons.battery)
            charging_status = "Battery"

        # Set a descriptive tooltip with battery percentage
        self.set_tooltip_markup(f"{charging_status}" if not data.VERTICAL else f"{charging_status}: {percentage}%")
