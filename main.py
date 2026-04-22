from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

from .actions.LaunchGame.LaunchGame import LaunchGame
from .actions.ToggleBigPicture.ToggleBigPicture import ToggleBigPicture

class SteamPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.launch_game_holder = ActionHolder(
            plugin_base = self,
            action_base = LaunchGame,
            action_id = "steam::LaunchGame",
            action_name = "Launch Steam Game",
        )
        self.add_action_holder(self.launch_game_holder)

        self.toggle_bp_holder = ActionHolder(
            plugin_base = self,
            action_base = ToggleBigPicture,
            action_id = "steam::ToggleBigPicture",
            action_name = "Toggle Big Picture",
        )
        self.add_action_holder(self.toggle_bp_holder)

        self.register(
            plugin_name = "Steam Games",
            github_repo = "https://github.com/StreamController/SteamPlugin",
            plugin_version = "1.0.2",
            app_version = "1.1.1-alpha"
        )

