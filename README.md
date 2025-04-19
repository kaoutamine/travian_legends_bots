# Automate your Travian gameplay like a pro 
## - while not being an obvious bot.
This project connects directly to Travian’s servers through clean, fast API calls — no browsers, no slow clicking bots.
If you know a little Python, can run a few scripts, and don’t mind answering some simple terminal questions, you can fully automate your early-game oasis raiding in minutes.
Fast, stealthy, expandable — built by players, for players.


## API method by reverse engineering logins with Burp Suite/Inspect, storing variables and making API requests

### `login.py`:
- Loads credentials (`TRAVIAN_EMAIL` and `TRAVIAN_PASSWORD`) from a `.env` file, creating it if missing.
- Logs into Travian using the PKCE OAuth2 flow.
- Retrieves active avatars and servers via GraphQL.
- Lets you choose the server to connect to from a terminal menu.

---

### `oasis_raiding_main.py` (current working automation):

✅ After logging in and selecting the server and village, the script:
1. **Loads your villages** from your identity card (`identity.json`) and selects one.
2. **Loads a full map scan** previously saved.
3. **Parses all unoccupied oases** (true unowned "Unoccupied oasis" only).
4. **Asks how many troops you want to send per raid** (example: 6 Equites Imperatoris).
5. **Raids only the available unoccupied oases**, respecting your available troop count.
6. **Handles the Travian checksum** to validate attack sending.
7. **Stops raiding automatically when you run out of troops**.

---

### `check_sum_attack_breaking_script.py` (Proof of Concept):
- **Extracts and correctly injects the Travian checksum** needed to validate manual troop attacks.
- **Bypasses the normal UI interaction checks** using API calls and looks like a legit human interaction.
- **Now fully integrated into the main raiding logic**.

---

### `full_map_scanning_main.py`:
- **Scans a full radius** around the selected village (default 25x25 tiles).
- **Saves detailed metadata and tile information** (including oases, wilderness, villages) into a timestamped JSON database.
- Used to build your personal local oasis database.

---

### `database/identity_manager.py`:
- **Handles the player's "identity card"**:
  - Stores all servers, villages, and village coordinates.
  - Avoids re-asking for data if already known.
- Used as a reference for automations instead of hardcoding values.

---

### Architecture Progress:
- 🛠️ Modular structure: `identity_handling/`, `database/`, `full_map_scanning/`, `oasis_raiding/`.
- ✅ No browser or Selenium needed: pure fast API calls.
- ✅ All project data is now neatly structured and reused.
- ✅ Designed for easy expansions (different types of farms, hero raiding, player tracking).

---

## Next Steps

## Next Steps

### 🖥 Usability Improvements
- 🛠 **Fuse everything into one seamless script**: from login → map scan → oasis selection → raid sending.
- 🔁 **Integrate into a self-running script**:
  - Auto-login, auto-map-scan, auto-update raids periodically.
- 📦 **Package as a desktop application**:
  - Make it accessible for non-Python, non-technical users (e.g., using PyInstaller or BeeWare).

### 🛡 Robustness and Adaptability
- 🧪 **Extensively verify adaptability to another player**:
  - Fresh clone testing has already been tried so there shouldn't be much issues there.
  - More real-world tests with different accounts are needed.
- ⚠️ **Handle multi-server players**:
  - Right now, assumes **only one active server**.
  - Would need **database separation** between servers for identity cards and full scan maps.
- 🏡 **Handle multi-village players**:
  - Right now, optimized for **one-village setups**.
  - Would require adapting the database to **track villages separately**, and manage troop availability per village.

### 🎮 Extra Gaming Features
- 🦸 **Hero Smart Raiding module**:
  - Identify **weak oases** suitable for solo hero XP farming.
  - Calculate **safe troop compositions** (minimize or eliminate troop losses).
  - Automatically target low-risk, high-reward oases intelligently.



## The selenium attempt was an easier way to automatise a workflow by using the firefox plugin to replicate specific actions
This attempt yielded interesting results but it prevented me from doing calculations, scans and automating more things. 
The idea was to use a browser to connect to Travian and then replicate
a specific path using the Selenium plugin (works only on firefox these days) to for example launch the raid lists in Travian.
It worked but ignore it. It's slow and it does only what a human could do. We can do better.




---

