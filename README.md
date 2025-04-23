# 🚀 Travian API Automation Project
## 🛠 Personal Reverse Engineering and Automation

---

> *Built out of curiosity, for personal use, and as an engineering challenge.* ⚙️

> A full early-game flow from login to launching raids.

---

## 🔑 1. Login and Find Your Villages

Login securely with your `.env` credentials.  
Auto-fetch all your linked **avatars** and **villages**.

![Login and villages](https://github.com/user-attachments/assets/ad070b81-82b2-4ed3-80f6-2df92ab69a22)

---

## 🗺 2. Scan the Map Around Your Village

Quickly scan thousands of tiles to detect nearby oases.  
(✅ Everything saved locally for fast reuse later.)

![Scanning](https://github.com/user-attachments/assets/e1625431-6b16-46b9-893a-9eeb0f18712f)

---

## 🏕 3. Map and Number All Unoccupied Oases

List unoccupied oases around you —  
sorted automatically by distance for smarter raiding.

![Oases numbering](https://github.com/user-attachments/assets/87effc3a-8f4c-4ec3-be9c-081c05a5861d)

---

## ⚔️ 4. Pick the Troops You Want to Raid With

Choose your unit type (e.g., Equites Imperatoris)  
and define how many troops per raid.

![Unit code for raid](https://github.com/user-attachments/assets/71d7e71b-0e1e-4f83-bd37-26a711d51cdd)

---

## 🚀 5. Launch Raids Automatically

The bot sends raids intelligently:  
✅ Only unoccupied oases  
✅ Closest first  
✅ Stops automatically when no more troops left

![Launching raids](https://github.com/user-attachments/assets/6f3dd4a1-fe05-4186-900b-6d99be89da99)

---

## HOW TO USE THE SCRIPT
I designed this script for myself. I designed it to scale but as you know without testing it probably won't work for someone else from the get go.
I'm sorry for this. Please contact me for debug.

1) git clone this repository 
2) **IMPORTANT** Place yourself in the travian_bot file.
```bash
cd travian_legend_bots/API_based_automations/travian_bot
```
4) run python3 map_scanning_main.py, fill in your email & password. they will be saved to a .env file. Do a scan. It will be saved in a database/ file with your identity and your villages.
```bash
python3 map_scanning_main.py
```
6) run python3 oasis_raiding_from_scan_list.py and fill in whatever is needed in there.
```bash
python3 oasis_raiding_from_scan_list.py
```
That's it! Hopefully you should have launched your first raid 🎫🎟️

---


**Background**:  
This project was created after spending a lot of time manually inspecting Travian’s network behavior using Burp Suite and browser developer tools.  
Travian uses a combination of:
- **GraphQL API requests** for dynamic data (like avatars, farm lists, account metadata).
- **Classic HTML endpoints** for legacy game views (e.g., `dorf1.php`, `dorf2.php`), where most of the world state is embedded into large static HTML pages.

Bot prevention primarily relies on hidden dynamic fields (tokens, checksums), not on traditional CAPTCHA systems.  
With careful parsing and request crafting, those mechanisms were bypassed reliably without trying to "spoof" a browser.

---

## 📚 Project Philosophy

This tool was never meant to be widely distributed:  
- It's a personal technical exercise — **a playground for reverse engineering, automation architecture, and real-world API handling**.
- It intentionally skips building a GUI to **stay lightweight and focus on code quality and expandability**.
- It's not intended to fully replace manual gameplay, only to **relieve repetitive tasks like early-game oasis farming**.

The idea is to automate *enough* to assist, but not so much that it kills the fun.

---

## 🛠 Typical Usage Flow (Single Village)

### Step 1 — Scan the Map
- Launch `map_scan_and_oasis_extract_main.py`.
- Enter login credentials once (saved in a local `.env` file, no 2FA needed).
- Select the scan radius (**example**: a 25-tile radius = ~2,500 tiles).
- Tiles are scanned at about **20 per second** to fly under bot detection radars (some functions of travian have similar scanning speed).
- After scanning, local JSON files are generated containing full map and oasis data in the database/ file. Per village.

### Step 2 — Launch Raids
- Launch `oasis_raiding_from_scan_list_main.py`.
- Village and available troops are automatically loaded.
- Troop allocation is automatic, for example for Romans you could specify (via the terminal)
  - First use **legionnaires** (groups of 20)  
  - Then use **Equites Imperatoris** (groups of 6)
- The script targets **only unoccupied oases without defenders** and raids **closest first**.

The flow is designed to stay minimal and resilient — no unnecessary prompts, no wasted actions.

---

## ⚡ Alternative Raiding (Optional)

There’s also a `oasis_raiding_from_raid_list_main.py` method based on pre-defined farm lists inside Travian.  
It’s functional, but scan-based raiding is currently faster and more reliable.

---

> This project is a side experiment in engineering clean, API-driven game interactions — not a "cheat" platform.  
> All contributions were made for **personal use** and **learning purposes only**.


# 🔥 Project Highlights
### If you want to dive into the technical side or understand the architecture

---

## 🧩 API-based Automation — Built by Reverse Engineering

Instead of interacting with the web UI, this project connects **directly to Travian's APIs** and **classic HTML endpoints**, carefully reconstructing all required requests and protections manually.

Travian uses:
- **Classic email/password authentication with an extra variable hidden in the request (Unclear what it's for)** for authentication.
- **GraphQL APIs** for account, avatar, and farm list management.
- **Classic POST/GET** forms and **HTML scraping** for troop movements and map interactions.
- **Dynamic bot protection fields** (tokens, checksums) inside forms that must be parsed and reused at every interaction.

All major obstacles were handled cleanly:
- **OAuth token acquisition** through code verifier/challenge flow.
- **Session maintenance** via cookies between lobby and gameworld.
- **Checksum generation/extraction** for attack requests.
- **Anti-bot measures** bypassed by scraping dynamic fields and replaying them properly.

---

## 📂 `identity_handling/login.py` — Account Handling

- Loads your Travian credentials safely from a local `.env` file.
- If missing, prompts once and auto-creates the file.
- Handles full **OAuth2 PKCE flow** without using a browser.
- Lists all active avatars (accounts) linked to your identity.
- Lets you **choose the target server** (or hardcode default selection).
- After login, **hands over an authenticated Session object** for further API calls.

---

## ⚔️ `oasis_raiding_from_scan_list_main.py` — Fully Automated Oasis Raiding

✅ Once logged in, the script:
1. **Loads your village data** (ID, coordinates) from an internal **identity card** JSON.
2. **Fetches your live troop count** directly from `dorf1.php`, parsing HTML.
3. **Loads the most recent full map scan** locally saved.
4. **Filters** only real "Unoccupied oases" (ignores wilderness and fake targets).
5. **Ranks oases by proximity** (closest first) based on tile coordinates.
6. **Skips oases with any animal defenders**, checking before each raid.
7. **Handles attack checksum fields dynamically**, to pass bot protection.
8. **Sends small raiding parties** (e.g., 20 Legionnaires, 6 Equites Imperatoris) intelligently until troops run out.

Notes:
- Delays between attacks are randomized (**0.5s - 1.2s**) to simulate human behavior.
- Server responses are validated at every step to ensure stability.

---

## 🗺️ `full_scan_oasis_analysis.py` — Map Scanning and Database

- Scans the map in a **configurable radius** (default: 25 tiles = 2,500+ tiles).
- Works by sending **map position GraphQL queries** systematically.
- Parses and saves **tile metadata** (type, ownership, bonuses, coordinates).
- After scanning:
  - Automatically extracts **unoccupied oases**.
  - Saves them in **timestamped JSON** files inside a dedicated folder.
  - Stores metadata (scan date, center coordinates, scan radius) for traceability.

---

## 🔧 `core/travian_api.py` — API Wrapper

Central module abstracting all Travian server interactions:
- **Authentication flows** (login, token handling, session management).
- **Troop data scraping** from `dorf1.php`.
- **Farm list management**: creating, listing, sending raids.
- **Oasis attack preparation and execution**:
  - Fetches necessary checksums.
  - Prepares attack payloads.
  - Sends authenticated POST requests matching expected client behavior.
- **Map interaction** through **GraphQL** queries:
  - Fetch tile metadata.
  - Analyze surrounding map.
  - Discover villages, oases, wilderness tiles.

All functions are built:
- **Idempotent**: safe to retry.
- **Modular**: reusable from anywhere.
- **Compatible** with future expansions (hero automation, multi-village support).

---

# 🛠 Engineering Design Choices

- **No browser automation** (Selenium/Playwright) — 100% API-driven.
- **No hard dependencies** outside `requests`, `bs4`, and `python-dotenv`.
- **Minimal external libraries** for security, portability, and long-term maintainability.
- **Separation of concerns**: login logic, API wrapper, map scanning, oasis management all live in distinct modules.
- **Extensibility ready**: easily pluggable into more complex automation (resource management, construction queues, etc.).

---

### `proof_of_concepts/`:

- Testing playgrounds to experiment with attacks, map reads, checksum injections, etc.

---

### ✅ Summary

- No browser automation needed (no Selenium, no ChromeDriver).
- Clean, fast, human-like interactions with the server.
- Modular code, easy to expand into **full automation**.

---

# 🏗 Current Project Structure

```markdown
📂 Project Structure

├── API_based_automations
│   ├── readme.md
│   └── travian_bot
│       ├── __pycache__
│       ├── analysis
│       ├── core
│       ├── database
│       ├── identity_handling
│       ├── map_scanning_main.py
│       ├── oasis_raiding_from_raid_list_main.py
│       ├── oasis_raiding_from_scan_list_main.py
│       ├── proof_of_concepts
│       ├── refactor_attempt
│       └── requirements.txt
├── README.md
├── selenium_UI based_exploits
│   ├── VillageOasisRaidRecording.py
│   ├── gettingCookies.py
│   ├── seleniumTest.py
│   └── test_TravianVillagesRaidFirefox.py
└── structure.txt
```
---


# 🔥 Current Achievements

- Fully API-driven Travian automation.
- No browser or Selenium needed.
- Travian checksum bypass integrated.
- Smart oasis targeting (no animals, closest first).
- Self-updating local data structure.

---

# 🧩 What's Coming Next?

## 🖥 Usability Improvements
- Fuse login → map scan → oasis raid into one seamless script.
- Add self-refreshing scripts (auto rescan, auto raid).
- Package into a desktop app for non-tech users.

---

## 💡 Contributing to this Project

1. Fork the repo
2. Create a feature branch (`git checkout -b my-feature`)
3. Commit your changes
4. Push to your fork
5. Open a Pull Request to the `main` branch of this repo

All contributions go through PR review. Thank you!

---

## 🛡 Robustness Enhancements
- Better support for multi-account and multi-server players.
- Handle multi-village troop management.
- Build auto-recovery in case of API/login errors.

---

## 🎮 Extra Features
- Hero smart raiding (weak oasis auto-pick for hero XP).
- Troop stat scraping for smarter raid planning.

---

# 🕹 Bonus (Old Method)

Inside `selenium_UI based_exploits/`:
- Early experiments using Selenium + Firefox action replay.
- Deprecated in favor of superior API-only approach.

---

# 🎯 Why Use This?

- It's way faster than clicking manually.
- Looks exactly like a real human player.
- Gives you real strategic data.
- Expandable into anything: construction, attacking, farming.

---

# ✨ Happy Raiding!

