from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os
import subprocess

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib

from ...steam_utils import get_steam_library


class ToggleBigPicture(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()
        self._last_state = None  # (is_running, is_bp_active)

    def on_ready(self) -> None:
        self._last_state = None
        self._update_visual_state()

    def _current_state(self):
        running = self.steam_library.is_steam_running()
        bp = self.steam_library.is_big_picture_active() if running else False
        return (running, bp)

    def _update_visual_state(self):
        settings = self.get_settings()
        start_in_bp = settings.get("start_in_bp", True)

        running, bp = self._current_state()
        self._last_state = (running, bp)

        if not running:
            icon_name = "bp_off_bigpicture.png" if start_in_bp else "bp_off_normal.png"
        elif bp:
            icon_name = "bp_bigpicture.png"
        else:
            icon_name = "bp_normal.png"

        icon_path = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        self.set_media(media_path=icon_path, size=0.75)

    def on_tick(self) -> None:
        """Called every second — refresh icon only if state changed"""
        current = self._current_state()
        if current != self._last_state:
            self._last_state = current
            self._update_visual_state()

    def on_key_down(self) -> None:
        if not self.steam_library.is_steam_running():
            # Steam is off: launch in the configured mode
            settings = self.get_settings()
            if settings.get("start_in_bp", True):
                self.steam_library.open_big_picture()
            else:
                subprocess.Popen(['steam'],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            GLib.timeout_add(3000, self._delayed_update)
        elif self.steam_library.is_big_picture_active():
            # Currently in Big Picture → switch to normal desktop mode
            self.steam_library.minimize_steam()
            GLib.timeout_add(1500, self._delayed_update)
        else:
            # Normal mode → open Big Picture
            self.steam_library.open_big_picture()
            GLib.timeout_add(3000, self._delayed_update)

    def _delayed_update(self):
        self._update_visual_state()
        return False

    def on_key_up(self) -> None:
        pass

    def get_config_rows(self) -> list:
        self.start_mode_switch = Adw.SwitchRow(
            title="Start in Big Picture",
            subtitle="When Steam is closed, open it directly in Big Picture mode"
        )
        settings = self.get_settings()
        self.start_mode_switch.set_active(settings.get("start_in_bp", True))
        self.start_mode_switch.connect("notify::active", self._on_start_mode_changed)
        return [self.start_mode_switch]

    def _on_start_mode_changed(self, switch, *args):
        settings = self.get_settings()
        settings["start_in_bp"] = switch.get_active()
        self.set_settings(settings)
