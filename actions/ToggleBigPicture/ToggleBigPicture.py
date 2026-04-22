from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from ...steam_utils import get_steam_library


class ToggleBigPicture(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()
        self.checking_state = False

    def on_ready(self) -> None:
        """Called when the action is ready"""
        self._update_visual_state()

    def _update_visual_state(self):
        """Updates the visual state of the button based on Steam status"""
        if self.steam_library.is_steam_running():
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
        else:
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "steam_off.png")

        self.set_media(media_path=icon_path, size=0.75)

    def on_key_down(self) -> None:
        """Called when the key is pressed"""
        settings = self.get_settings()
        action_mode = settings.get("action_mode", "toggle")

        if action_mode == "toggle":
            self._toggle_big_picture()
        elif action_mode == "open":
            self._open_big_picture()
        elif action_mode == "close":
            self._close_steam()

    def _toggle_big_picture(self):
        """Toggles between Big Picture active and Steam closed/minimized"""
        is_bp_active = self.steam_library.is_big_picture_active()

        print(f"[ToggleBigPicture] Big Picture status: {is_bp_active}")

        if is_bp_active:
            close_mode = self.get_settings().get("close_mode", "minimize")
            if close_mode == "close":
                self.steam_library.close_steam()
            else:
                self.steam_library.minimize_steam()

            GLib.timeout_add(1500, self._delayed_update)
        else:
            self.steam_library.open_big_picture()

            GLib.timeout_add(3000, self._delayed_update)

    def _open_big_picture(self):
        """Opens Big Picture mode only"""
        self.steam_library.open_big_picture()
        GLib.timeout_add(3000, self._delayed_update)

    def _close_steam(self):
        """Closes Steam only"""
        close_mode = self.get_settings().get("close_mode", "minimize")

        if close_mode == "close":
            self.steam_library.close_steam()
        else:
            self.steam_library.minimize_steam()

        GLib.timeout_add(1500, self._delayed_update)

    def _delayed_update(self):
        """Updates the visual state after a delay"""
        self._update_visual_state()
        return False

    def on_key_up(self) -> None:
        """Called when the key is released"""
        pass

    def get_config_rows(self) -> list:
        """Returns configuration rows for the UI"""
        self.action_mode_row = Adw.ComboRow(title="Action Mode")
        action_modes = Gtk.StringList()
        action_modes.append("Toggle Big Picture ↔ Close")
        action_modes.append("Open Big Picture Only")
        action_modes.append("Close Steam Only")
        self.action_mode_row.set_model(action_modes)

        self.close_mode_row = Adw.ComboRow(
            title="Close Mode",
            subtitle="What to do when closing Steam"
        )
        close_modes = Gtk.StringList()
        close_modes.append("Minimize (hide window)")
        close_modes.append("Close completely")
        self.close_mode_row.set_model(close_modes)

        self._load_config_values()

        self.action_mode_row.connect("notify::selected", self.on_action_mode_changed)
        self.close_mode_row.connect("notify::selected", self.on_close_mode_changed)

        return [self.action_mode_row, self.close_mode_row]

    def _load_config_values(self):
        """Loads current configuration values"""
        settings = self.get_settings()
        action_mode = settings.get("action_mode", "toggle")
        close_mode = settings.get("close_mode", "minimize")

        action_mode_map = {"toggle": 0, "open": 1, "close": 2}
        close_mode_map = {"minimize": 0, "close": 2}

        self.action_mode_row.set_selected(action_mode_map.get(action_mode, 0))
        self.close_mode_row.set_selected(close_mode_map.get(close_mode, 0))

    def on_action_mode_changed(self, combo, *args):
        """Called when action mode changes"""
        selected_idx = combo.get_selected()

        mode_map = {0: "toggle", 1: "open", 2: "close"}

        if selected_idx in mode_map:
            settings = self.get_settings()
            settings["action_mode"] = mode_map[selected_idx]
            self.set_settings(settings)

    def on_close_mode_changed(self, combo, *args):
        """Called when close mode changes"""
        selected_idx = combo.get_selected()

        mode_map = {0: "minimize", 2: "close"}

        if selected_idx in mode_map:
            settings = self.get_settings()
            settings["close_mode"] = mode_map[selected_idx]
            self.set_settings(settings)

