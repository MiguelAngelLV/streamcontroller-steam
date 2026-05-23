from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib

from ...steam_utils import get_steam_library, _run_check


class CloseSteam(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()
        self._last_running = None  # track state for on_tick

    def on_ready(self) -> None:
        """Called when the action is ready"""
        self._last_running = None
        self._update_visual_state()

    def _update_visual_state(self):
        """Updates the button icon based on whether Steam is running"""
        if self.steam_library.is_steam_running():
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "steam.png")
        else:
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "steam_off.png")

        self.set_media(media_path=icon_path, size=0.75)

    def on_key_down(self) -> None:
        """Called when the key is pressed"""
        if not self.steam_library.is_steam_running():
            return

        settings = self.get_settings()
        close_mode = settings.get("close_mode", "clean")

        if close_mode == "clean":
            # Clean shutdown via `steam -shutdown`
            success = self.steam_library.close_steam()
        else:
            # Force kill via pkill
            try:
                _run_check(["pkill", "-9", "steam"])
                success = True
            except Exception as e:
                print(f"[CloseSteam] Error force-killing Steam: {e}")
                success = False

        if success:
            # Wait a moment before updating the icon
            GLib.timeout_add(2000, self._delayed_update)

    def _delayed_update(self):
        self._update_visual_state()
        return False

    def on_key_up(self) -> None:
        """Called when the key is released"""
        pass

    def get_config_rows(self) -> list:
        """Returns configuration rows for the UI"""
        self.close_mode_row = Adw.ComboRow(
            title="Close Mode",
            subtitle="How to close Steam"
        )
        close_modes = Gtk.StringList()
        close_modes.append("Clean shutdown (steam -shutdown)")
        close_modes.append("Force kill (pkill -9)")
        self.close_mode_row.set_model(close_modes)

        self._load_config_values()
        self.close_mode_row.connect("notify::selected", self.on_close_mode_changed)

        return [self.close_mode_row]

    def _load_config_values(self):
        settings = self.get_settings()
        close_mode = settings.get("close_mode", "clean")
        mode_map = {"clean": 0, "force": 1}
        self.close_mode_row.set_selected(mode_map.get(close_mode, 0))

    def on_close_mode_changed(self, combo, *args):
        selected_idx = combo.get_selected()
        mode_map = {0: "clean", 1: "force"}
        if selected_idx in mode_map:
            settings = self.get_settings()
            settings["close_mode"] = mode_map[selected_idx]
            self.set_settings(settings)

    def on_tick(self) -> None:
        """Called every second — update icon if Steam running state changed"""
        running = self.steam_library.is_steam_running()
        if running != self._last_running:
            self._last_running = running
            self._update_visual_state()
