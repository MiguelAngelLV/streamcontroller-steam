from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder


from .actions.LaunchGame.LaunchGame import LaunchGame
from .actions.ToggleBigPicture.ToggleBigPicture import ToggleBigPicture
from .actions.CloseSteam.CloseSteam import CloseSteam
from .actions.ChangeStatus.ChangeStatus import ChangeStatus
from .actions.OpenSteamPage.OpenSteamPage import OpenSteamPage
from .actions.TakeScreenshot.TakeScreenshot import TakeScreenshot

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

        self.close_steam_holder = ActionHolder(
            plugin_base = self,
            action_base = CloseSteam,
            action_id = "steam::CloseSteam",
            action_name = "Close Steam",
        )
        self.add_action_holder(self.close_steam_holder)

        self.change_status_holder = ActionHolder(
            plugin_base = self,
            action_base = ChangeStatus,
            action_id = "steam::ChangeStatus",
            action_name = "Change Steam Status",
        )
        self.add_action_holder(self.change_status_holder)

        self.open_page_holder = ActionHolder(
            plugin_base = self,
            action_base = OpenSteamPage,
            action_id = "steam::OpenSteamPage",
            action_name = "Open Steam Page",
        )
        self.add_action_holder(self.open_page_holder)

        self.take_screenshot_holder = ActionHolder(
            plugin_base = self,
            action_base = TakeScreenshot,
            action_id = "steam::TakeScreenshot",
            action_name = "Take Steam Screenshot",
        )
        self.add_action_holder(self.take_screenshot_holder)

        self.register(
            plugin_name = "Steam Games",
            github_repo = "https://github.com/StreamController/SteamPlugin",
            plugin_version = "1.0.2",
            app_version = "1.1.1-alpha"
        )

