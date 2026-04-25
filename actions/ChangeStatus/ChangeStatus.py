from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

import os

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GLib

from ...steam_utils import get_steam_library

# Ordered cycle: online → away → invisible → offline → online …
STATUS_KEYS = ["online", "away", "invisible", "offline"]

STATUS_ICONS = {
    "online":    "status_online.png",
    "away":      "status_away.png",
    "invisible": "status_invisible.png",
    "offline":   "status_offline.png",
    "steam_off": "status_steam_off.png",   # Steam not running
}

STATUS_LABELS = {
    "online":    "Online",
    "away":      "Away",
    "invisible": "Invisible",
    "offline":   "Offline",
    "steam_off": "Steam off",
}

DEBOUNCE_MS = 1000  # ms to wait before sending command to Steam


class ChangeStatus(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.steam_library = get_steam_library()
        self._displayed_idx = 0
        self._pending_timeout_id = None
        self._last_running = None
        self._last_status = None  # last known Steam status key

    def on_ready(self) -> None:
        # Cancel any pending debounce timer left over from before a page navigation
        if self._pending_timeout_id is not None:
            GLib.source_remove(self._pending_timeout_id)
            self._pending_timeout_id = None

        settings = self.get_settings()
        committed = settings.get("committed_status", "online")
        self._displayed_idx = STATUS_KEYS.index(committed) if committed in STATUS_KEYS else 0
        self._last_running = None
        self._last_status = None
        self._update_visual_state()

    # ------------------------------------------------------------------ visuals

    def _displayed_status(self) -> str:
        return STATUS_KEYS[self._displayed_idx]

    def _update_visual_state(self, key: str = None):
        """Render icon + label for the given status key (defaults to displayed)."""
        if key is None:
            key = self._displayed_status() if self.steam_library.is_steam_running() else "steam_off"

        icon_name = STATUS_ICONS.get(key, STATUS_ICONS["steam_off"])
        icon_path = os.path.join(self.plugin_base.PATH, "assets", icon_name)
        self.set_media(media_path=icon_path, size=0.75)
        self.set_bottom_label(STATUS_LABELS.get(key, ""), font_size=11)

    # ------------------------------------------------------------------ input

    def on_key_down(self) -> None:
        if not self.steam_library.is_steam_running():
            return  # Do nothing when Steam is off

        # Cancel any running debounce timer
        if self._pending_timeout_id is not None:
            GLib.source_remove(self._pending_timeout_id)
            self._pending_timeout_id = None

        # Advance displayed status to the next one in the cycle
        self._displayed_idx = (self._displayed_idx + 1) % len(STATUS_KEYS)
        self._update_visual_state()

        # Schedule the actual Steam command after DEBOUNCE_MS
        self._pending_timeout_id = GLib.timeout_add(DEBOUNCE_MS, self._apply_status)

    def on_key_up(self) -> None:
        pass

    def _apply_status(self) -> bool:
        """Called after the debounce delay — sends the status to Steam."""
        status = self._displayed_status()
        self.steam_library.change_status(status)

        # Persist the committed status so on_ready restores it correctly
        settings = self.get_settings()
        settings["committed_status"] = status
        self.set_settings(settings)

        self._pending_timeout_id = None
        return False  # Don't repeat

    def on_tick(self) -> None:
        """Called every second — sync icon with actual Steam status."""
        running = self.steam_library.is_steam_running()

        # Steam turned on or off
        if running != self._last_running:
            self._last_running = running
            if not running:
                self._last_status = None
                self._update_visual_state()
                return

        if not running:
            return

        # Steam is running: check actual status
        # Skip check if debounce is pending (user is cycling, don't overwrite display)
        if self._pending_timeout_id is not None:
            return

        current_status = self.steam_library.get_current_status()
        if current_status is not None and current_status != self._last_status:
            self._last_status = current_status
            if current_status in STATUS_KEYS:
                self._displayed_idx = STATUS_KEYS.index(current_status)
            self._update_visual_state()
