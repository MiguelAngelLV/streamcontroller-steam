# Steam Games Plugin for StreamController

A StreamController plugin that allows you to launch Steam games directly from your Stream Deck and control Steam Big Picture mode.

## Features

- 🎮 **Automatic game detection**: Automatically finds all installed Steam games on your system
- 🖼️ **Game icons**: Displays the official icon for each game on your Stream Deck
- 🎯 **Two launch modes**:
  - Normal game launch
  - Big Picture mode launch
- 🔄 **Big Picture control**: New action to easily open/close Big Picture mode
- 📚 **Multiple libraries**: Supports multiple Steam library folders
- 🔄 **Easy configuration**: Intuitive graphical interface for selecting games
- 🏠 **Automatic detection**: The installer detects whether you're using Flatpak or other installations

## Available Actions

### 1. Launch Steam Game
Launches a specific Steam game from your Stream Deck.

**Configuration:**
- Select the game from the dropdown menu
- Enable/disable Big Picture mode

**Functionality:**
- Displays the game icon on the button
- Shows the game name (truncated if too long)
- Press to launch the game
- Visual feedback: "Launching..." when pressed

### 2. Toggle Big Picture
Toggle between Big Picture active and Steam closed/minimized with a single button.

**Configuration:**
- **Action Mode**: 
  - Toggle Big Picture ↔ Close (recommended)
  - Open Big Picture Only
  - Close Steam Only
- **Close Mode**:
  - Close Big Picture
  - Close completely (shutdown Steam)

**Functionality:**
- Shows current status: "BP Active", "Steam Open", or "Steam Off"
- Single button to open and close Big Picture
- Ideal for controlling your gaming experience

## Requirements

- StreamController 1.1.1-alpha or higher
- Steam installed on Linux
- Python 3.8+
- GTK 4.0 and Adwaita

## Usage

### Launching a Game

1. In StreamController, drag the "Launch Steam Game" action to a button
2. In the configuration:
   - Select the game from the dropdown menu
   - (Optional) Enable "Big Picture Mode"
3. The game icon will appear automatically
4. Press the button to launch the game

### Controlling Big Picture

1. Drag the "Toggle Big Picture" action to a button
2. Configure the behavior:
   - **Toggle**: Opens Big Picture if closed, closes/minimizes if open
   - **Open Only**: Only opens Big Picture
   - **Close Only**: Only closes/minimizes Steam
3. Choose whether to exit from Big Picture or completely close Steam
4. Press the button to control Big Picture

## Project Structure

```
streamcontroller-steam/
├── main.py                     # Plugin entry point
├── manifest.json               # Plugin metadata
├── steam_utils.py              # Steam management utilities
├── actions/
│   ├── LaunchGame/
│   │   └── LaunchGame.py       # Game launch action
│   └── ToggleBigPicture/
│       └── ToggleBigPicture.py # Big Picture control action
└── assets/
    └── info.png               # Default icon
```

## Development

### Game Detection

The plugin detects Steam games through:

1. Locating the Steam installation folder
2. Reading the `libraryfolders.vdf` file to find all libraries
3. Parsing `.acf` files in each `steamapps/` folder to get installed game information
4. Filtering system tools (Proton, runtimes)
5. Removing duplicates when there are multiple libraries
6. Extracting icons from `appcache/librarycache/` or downloading from Steam CDN

### Game Launching

Games are launched using the Steam URL protocol:
- Normal: `steam://rungameid/{APP_ID}`
- Big Picture: `steam://open/bigpicture/steam://rungameid/{APP_ID}`

### Big Picture Control

The plugin can:
- Check if Steam is running
- Detect if Big Picture is active 
- Open Big Picture
- Close Big Picture
- Close Steam

## License

See LICENSE file for details.

## Contributions

Contributions are welcome. Please open an issue or pull request on GitHub.


