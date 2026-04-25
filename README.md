# Steam Plugin for StreamController

Control Steam directly from your Stream Deck. 

Launch games, toggle Big Picture mode, change your online status, open Steam pages, take screenshots, and more — all with customizable buttons.

---

## Actions

### 🎮 Launch Game
Launches any installed Steam game with one button press.

- Automatically detects all installed games across multiple Steam libraries
- Shows the official game icon and name on the key
- Optional: launch directly in Big Picture mode

---

### 📺 Toggle Big Picture
Smart toggle: opens or closes Big Picture depending on the current state.

- Icon reflects real state: Steam off / normal mode / Big Picture active
- Configure whether pressing it while Steam is off opens it in Big Picture or desktop mode

---

### 😶 Change Status
Cycles through online statuses with each press: **Online → Away → Invisible → Offline → …**

- Debounced: waits 1 second after the last press before sending the command to Steam, so you can cycle faster without intermediate calls
- Shows the current status label on the key
- Syncs automatically with the real Steam status when idle

---

### 🌐 Open Steam Page
Opens a specific Steam section in one press.

Available pages: **Store · Friends · Downloads · News · Screenshots**

---

### 📸 Take Screenshot
Triggers a Steam screenshot of the current game. Shows a 📸 flash feedback on the key.

---

### ❌ Close Steam
Closes Steam from the deck.

- **Clean shutdown** (`steam -shutdown`) — recommended
- **Force kill** (`pkill -9`) — for when Steam is unresponsive
- 
---

## License

See [LICENSE](LICENSE) for details.
