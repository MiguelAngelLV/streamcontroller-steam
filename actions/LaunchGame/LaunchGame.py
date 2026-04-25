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


class LaunchGame(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()

    def on_ready(self) -> None:
        """Called when the action is ready"""
        settings = self.get_settings()
        app_id = settings.get("app_id", "")

        if app_id:
            icon_path = self.steam_library.get_game_icon_path(app_id)

            if icon_path and icon_path.exists():
                self.set_media(media_path=str(icon_path), size=1.0)
            else:
                default_icon = os.path.join(self.plugin_base.PATH, "assets", "steam.png")
                self.set_media(media_path=default_icon, size=0.75)

            game_name = settings.get("game_name", "")
            if game_name:
                if len(game_name) > 15:
                    label = game_name[:12] + "..."
                else:
                    label = game_name
                self.set_bottom_label(label, font_size=12)
        else:
            default_icon = os.path.join(self.plugin_base.PATH, "assets", "steam.png")
            self.set_media(media_path=default_icon, size=0.75)
            self.set_bottom_label("No Game", font_size=12)

    def on_key_down(self) -> None:
        """Called when the key is pressed"""
        settings = self.get_settings()
        app_id = settings.get("app_id", "")
        big_picture = settings.get("big_picture", False)

        if app_id:
            self.set_center_label("Launching...", font_size=10)

            success = self.steam_library.launch_game(app_id, big_picture)

            if not success:
                self.set_center_label("Error!", font_size=12)

    def on_key_up(self) -> None:
        """Called when the key is released"""
        self.set_center_label("", font_size=12)

    def get_config_rows(self) -> list:
        """Returns configuration rows for the UI"""
        self.game_combo = Adw.ComboRow(title="Game")
        self.big_picture_switch = Adw.SwitchRow(
            title="Big Picture Mode",
            subtitle="Launch game in Big Picture mode"
        )

        self._load_games()
        self._load_config_values()

        self.game_combo.connect("notify::selected", self.on_game_changed)
        self.big_picture_switch.connect("notify::active", self.on_big_picture_changed)

        return [self.game_combo, self.big_picture_switch]

    def _load_games(self):
        """Loads the list of installed games into the ComboRow"""
        games = self.steam_library.get_installed_games()

        game_names = Gtk.StringList()
        self.game_list = []

        for game in games:
            game_names.append(game.name)
            self.game_list.append({
                'app_id': game.app_id,
                'name': game.name
            })

        self.game_combo.set_model(game_names)

    def _load_config_values(self):
        """Loads current configuration values"""
        settings = self.get_settings()
        app_id = settings.get("app_id", "")
        big_picture = settings.get("big_picture", False)

        selected = False
        if app_id:
            for idx, game in enumerate(self.game_list):
                if game['app_id'] == app_id:
                    self.game_combo.set_selected(idx)
                    selected = True
                    break

        if not selected and len(self.game_list) > 0:
            self.game_combo.set_selected(0)
            settings["app_id"] = self.game_list[0]['app_id']
            settings["game_name"] = self.game_list[0]['name']
            self.set_settings(settings)
            self.on_ready()

        self.big_picture_switch.set_active(big_picture)

    def on_game_changed(self, combo, *args):
        """Called when game selection changes"""
        selected_idx = combo.get_selected()

        if selected_idx == Gtk.INVALID_LIST_POSITION or selected_idx >= len(self.game_list):
            return

        if 0 <= selected_idx < len(self.game_list):
            game = self.game_list[selected_idx]
            settings = self.get_settings()
            settings["app_id"] = game['app_id']
            settings["game_name"] = game['name']
            self.set_settings(settings)

            self.on_ready()

    def on_big_picture_changed(self, switch, *args):
        """Called when Big Picture switch changes"""
        settings = self.get_settings()
        settings["big_picture"] = switch.get_active()
        self.set_settings(settings)

