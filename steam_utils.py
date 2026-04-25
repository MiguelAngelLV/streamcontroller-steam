"""
Utilities for detecting and managing installed Steam games
"""
import re
import subprocess
import urllib.request
import tempfile
from pathlib import Path
from typing import List, Dict, Optional


class SteamGame:
    """Represents a Steam game"""
    def __init__(self, app_id: str, name: str, install_dir: str = ""):
        self.app_id = app_id
        self.name = name
        self.install_dir = install_dir

    def __repr__(self):
        return f"SteamGame(app_id={self.app_id}, name={self.name})"


class SteamLibrary:
    """Manages Steam game detection and library reading"""

    def __init__(self):
        self.steam_path = self._find_steam_path()
        self.library_folders = []
        if self.steam_path:
            self.library_folders = self._find_library_folders()

    def _find_steam_path(self) -> Optional[Path]:
        """Finds the Steam installation path"""
        possible_paths = [
            Path.home() / ".steam" / "steam",
            Path.home() / ".local" / "share" / "Steam",
            Path("/usr/share/steam"),
            Path("/usr/local/share/steam"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def _find_library_folders(self) -> List[Path]:
        """Finds all Steam library folders"""
        library_folders = []

        if not self.steam_path:
            return library_folders

        library_folders.append(self.steam_path)

        vdf_path = self.steam_path / "steamapps" / "libraryfolders.vdf"

        if vdf_path.exists():
            try:
                with open(vdf_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                path_pattern = re.compile(r'"path"\s+"([^"]+)"')
                for match in path_pattern.finditer(content):
                    library_path = Path(match.group(1))
                    if library_path.exists() and library_path not in library_folders:
                        library_folders.append(library_path)
            except Exception as e:
                print(f"Error reading libraryfolders.vdf: {e}")

        return library_folders

    def _parse_acf_file(self, acf_path: Path) -> Optional[Dict]:
        """Parses a Steam .acf manifest file"""
        try:
            with open(acf_path, 'r', encoding='utf-8') as f:
                content = f.read()

            app_id_match = re.search(r'"appid"\s+"(\d+)"', content)
            name_match = re.search(r'"name"\s+"([^"]+)"', content)
            install_dir_match = re.search(r'"installdir"\s+"([^"]+)"', content)

            if app_id_match and name_match:
                return {
                    'app_id': app_id_match.group(1),
                    'name': name_match.group(1),
                    'install_dir': install_dir_match.group(1) if install_dir_match else ''
                }
        except Exception as e:
            print(f"Error parsing {acf_path}: {e}")

        return None

    def get_installed_games(self) -> List[SteamGame]:
        """Gets a list of all installed games"""
        games_dict = {}

        system_app_ids = {
            '228980', '1070560', '1391110', '1628350',
            '2805730', '1493710', '1887720', '2348590', '2180100',
        }

        for library_folder in self.library_folders:
            steamapps_folder = library_folder / "steamapps"

            if not steamapps_folder.exists():
                continue

            for acf_file in steamapps_folder.glob("appmanifest_*.acf"):
                game_data = self._parse_acf_file(acf_file)

                if game_data:
                    app_id = game_data['app_id']

                    if app_id in system_app_ids:
                        continue

                    if 'proton' in game_data['name'].lower():
                        continue

                    if app_id not in games_dict:
                        game = SteamGame(
                            app_id=app_id,
                            name=game_data['name'],
                            install_dir=game_data['install_dir']
                        )
                        games_dict[app_id] = game

        games = list(games_dict.values())
        games.sort(key=lambda g: g.name.lower())

        return games

    def get_game_icon_path(self, app_id: str) -> Optional[Path]:
        """Gets the path to a game icon from Steam cache or downloads it"""
        if not self.steam_path:
            return None

        icon_cache = self.steam_path / "appcache" / "librarycache"

        if icon_cache.exists():
            icon_formats = [
                f"{app_id}_library_600x900.jpg",
                f"{app_id}_icon.jpg",
                f"{app_id}_logo.png",
                f"{app_id}_header.jpg",
                f"{app_id}_library_hero.jpg",
            ]

            for icon_name in icon_formats:
                icon_path = icon_cache / icon_name
                if icon_path.exists():
                    return icon_path

        return self._download_game_icon(app_id)

    def _download_game_icon(self, app_id: str) -> Optional[Path]:
        """Downloads a game icon from Steam CDN"""
        try:
            cache_dir = Path(tempfile.gettempdir()) / "streamcontroller_steam_cache"
            cache_dir.mkdir(exist_ok=True)

            icon_path = cache_dir / f"{app_id}_icon.jpg"

            if icon_path.exists():
                return icon_path

            cdn_urls = [
                f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/library_600x900.jpg",
                f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg",
                f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/capsule_184x69.jpg",
            ]

            for url in cdn_urls:
                try:
                    urllib.request.urlretrieve(url, icon_path)

                    if icon_path.exists() and icon_path.stat().st_size > 1000:
                        return icon_path
                except Exception:
                    continue

            if icon_path.exists():
                icon_path.unlink()

        except Exception as e:
            print(f"Error downloading icon for app {app_id}: {e}")

        return None

    def launch_game(self, app_id: str, big_picture: bool = False) -> bool:
        """Launches a Steam game"""
        try:
            if big_picture:
                url = f"steam://open/bigpicture/steam://rungameid/{app_id}"
            else:
                url = f"steam://rungameid/{app_id}"

            subprocess.Popen(['xdg-open', url],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error launching game {app_id}: {e}")
            return False

    def is_steam_running(self) -> bool:
        """Checks if Steam is running"""
        try:
            result = subprocess.run(['pgrep', '-x', 'steam'],
                                  capture_output=True,
                                  text=True)
            return result.returncode == 0
        except Exception:
            return False

    def is_big_picture_active(self) -> bool:
        """Checks if Big Picture mode is currently active by inspecting live window state."""

        # Method 1: wmctrl — list all windows and look for a Steam Big Picture window
        try:
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return 'big picture' in result.stdout.lower()
        except FileNotFoundError:
            pass  # wmctrl not installed, try next method
        except Exception as e:
            print(f"[is_big_picture_active] wmctrl failed: {e}")

        # Method 2: xdotool — query window names by Steam's X11 class
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--class', 'steam', 'getwindowname', '%@'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                return 'big picture' in result.stdout.lower()
        except FileNotFoundError:
            pass  # xdotool not installed
        except Exception as e:
            print(f"[is_big_picture_active] xdotool failed: {e}")

        return False

    def open_big_picture(self) -> bool:
        """Opens Steam Big Picture mode"""
        try:
            url = "steam://open/bigpicture"
            subprocess.Popen(['xdg-open', url],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error opening Big Picture: {e}")
            return False

    def minimize_steam(self) -> bool:
        """Minimizes Steam (hides from desktop)"""
        url = "steam://close/bigpicture"
        try:
            subprocess.run(['steam', url],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error minimizing Steam: {e}")
            return False

    def close_steam(self) -> bool:
        """Closes Steam completely"""
        try:
            subprocess.Popen(['steam', '-shutdown'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error closing Steam: {e}")
            return False

    def get_current_status(self) -> Optional[str]:
        """Reads the current Steam friend status.
        Returns 'online', 'away', 'invisible', 'offline', or None if undetectable.

        Detection order:
        1. loginusers.vdf → WantsOfflineMode=1  →  'offline'
           (ePersonaState is NOT updated when going offline, so this check comes first)
        2. localconfig.vdf → FriendStoreLocalPrefs → ePersonaState
           (1=online, 3=away, 7=invisible)
        """
        try:
            if not self.steam_path:
                return None

            # --- Step 1: Check WantsOfflineMode in loginusers.vdf ---
            loginusers_path = self.steam_path / "config" / "loginusers.vdf"
            if loginusers_path.exists():
                with open(loginusers_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lu_content = f.read()
                offline_match = re.search(r'"WantsOfflineMode"\s+"(\d+)"', lu_content)
                if offline_match and offline_match.group(1) == '1':
                    return 'offline'

            # --- Step 2: Read ePersonaState from localconfig.vdf ---
            # ePersonaState map (offline excluded — handled above)
            state_map = {1: 'online', 3: 'away', 7: 'invisible'}

            userdata_path = self.steam_path / "userdata"
            if not userdata_path.exists():
                return None

            user_dirs = [d for d in userdata_path.iterdir() if d.is_dir() and d.name.isdigit()]
            if not user_dirs:
                return None

            import json
            for user_dir in user_dirs:
                localconfig = user_dir / "config" / "localconfig.vdf"
                if not localconfig.exists():
                    continue

                with open(localconfig, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # FriendStoreLocalPrefs_<steamid> contains JSON with ePersonaState.
                # The value is a quoted string with \" escapes inside.
                match = re.search(
                    r'"FriendStoreLocalPrefs_\d+"\s+"((?:[^"\\]|\\.)*)"', content
                )
                if match:
                    try:
                        json_str = match.group(1).replace('\\"', '"')
                        data = json.loads(json_str)
                        state_int = data.get('ePersonaState')
                        if state_int is not None:
                            return state_map.get(int(state_int))
                    except (json.JSONDecodeError, ValueError):
                        pass
        except Exception as e:
            print(f"[get_current_status] Error: {e}")

        return None

    def change_status(self, status: str) -> bool:
        """Changes Steam friend status. status: 'online', 'away', 'invisible', 'offline'"""
        status_map = {
            'online':    'steam://friends/status/online',
            'away':      'steam://friends/status/away',
            'invisible': 'steam://friends/status/invisible',
            'offline':   'steam://friends/status/offline',
        }
        url = status_map.get(status)
        if not url:
            print(f"[change_status] Unknown status: {status}")
            return False
        try:
            subprocess.Popen(['xdg-open', url],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error changing status to {status}: {e}")
            return False

    def open_steam_page(self, page: str) -> bool:
        """Opens a Steam page. page: 'store', 'friends', 'downloads', 'news', 'screenshots'"""
        page_map = {
            'store':       'steam://open/store',
            'friends':     'steam://open/friends',
            'downloads':   'steam://open/downloads',
            'news':        'steam://open/news',
            'screenshots': 'steam://open/screenshots',
        }
        url = page_map.get(page)
        if not url:
            print(f"[open_steam_page] Unknown page: {page}")
            return False
        try:
            subprocess.Popen(['xdg-open', url],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error opening Steam page {page}: {e}")
            return False

    def take_screenshot(self) -> bool:
        """Triggers a Steam screenshot"""
        try:
            subprocess.Popen(['xdg-open', 'steam://screenshot'],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return False


_steam_library = None

def get_steam_library() -> SteamLibrary:
    """Gets the singleton instance of SteamLibrary"""
    global _steam_library
    if _steam_library is None:
        _steam_library = SteamLibrary()
    return _steam_library

