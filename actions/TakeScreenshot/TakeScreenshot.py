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


class TakeScreenshot(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()

    def on_ready(self) -> None:
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "screenshot.png")
        self.set_media(media_path=icon_path, size=0.75)

    def on_key_down(self) -> None:
        """Called when the key is pressed — triggers a Steam screenshot"""
        if not self.steam_library.is_steam_running():
            self.set_center_label("No Steam", font_size=10)
            GLib.timeout_add(1500, self._clear_label)
            return

        self.steam_library.take_screenshot()
        self.set_center_label("📸", font_size=18)
        GLib.timeout_add(800, self._clear_label)

    def _clear_label(self):
        self.set_center_label("", font_size=12)
        return False

    def on_key_up(self) -> None:
        pass

