from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

from ...steam_utils import get_steam_library

# Maps page key → (label, icon filename)
PAGE_CONFIG = {
    "store":       ("Store",       "store.png"),
    "friends":     ("Friends",     "friends.png"),
    "downloads":   ("Downloads",   "downloads.png"),
    "news":        ("News",        "news.png"),
    "screenshots": ("Screenshots", "screenshots_lib.png"),
}

PAGE_KEYS = ["store", "friends", "downloads", "news", "screenshots"]


class OpenSteamPage(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()

    def on_ready(self) -> None:
        self._update_visual_state()

    def _current_page(self) -> str:
        return self.get_settings().get("page", "store")

    def _update_visual_state(self):
        page = self._current_page()
        config = PAGE_CONFIG.get(page, PAGE_CONFIG["store"])
        icon_path = os.path.join(self.plugin_base.PATH, "assets", config[1])
        self.set_media(media_path=icon_path, size=0.75)
        self.set_bottom_label(config[0], font_size=11)

    def on_key_down(self) -> None:
        page = self._current_page()
        self.steam_library.open_steam_page(page)

    def on_key_up(self) -> None:
        pass

    def get_config_rows(self) -> list:
        self.page_row = Adw.ComboRow(title="Page to open")
        page_list = Gtk.StringList()
        for key in PAGE_KEYS:
            page_list.append(PAGE_CONFIG[key][0])
        self.page_row.set_model(page_list)

        self._load_config_values()
        self.page_row.connect("notify::selected", self.on_page_changed)

        return [self.page_row]

    def _load_config_values(self):
        page = self._current_page()
        idx = PAGE_KEYS.index(page) if page in PAGE_KEYS else 0
        self.page_row.set_selected(idx)

    def on_page_changed(self, combo, *args):
        idx = combo.get_selected()
        if 0 <= idx < len(PAGE_KEYS):
            settings = self.get_settings()
            settings["page"] = PAGE_KEYS[idx]
            self.set_settings(settings)
            self._update_visual_state()

