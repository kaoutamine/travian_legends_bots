# 🚀 Automate Your Travian Gameplay Like a Pro
## 🕵️ Stay Under the Radar — Play Smart

> *Automate smarter, not harder — your Travian empire just got a personal assistant.* 🌟

---

This project is intentionally left without a frontend for two reasons:
1. It’s not my wish to distribute this tool to just anyone — only to truly passionate players.
2. It’s not intended to fully replace raiding, but to act as a helper for repetitive tasks.

---

## 🛠 Typical Flow (Single Village)

**Step 1 — Scan the Map**  
Launch `map_scan_and_oasis_extract_main.py`.  
- Login credentials are requested once and safely stored in a `.env` file. (No 2FA in Travian.)  
- **Choose your scan radius carefully**: a 25-tile radius means scanning over **2,500 tiles**.  
- To stay stealthy, the bot scans at a rate of about **20 tiles per second**.  
- After scanning, data is stored in the database under folders named after **village coordinates**.  
- The system automatically extracts unoccupied oases from the scan.

**Step 2 — Launch Raids**  
Launch `oasis_raiding_from_scan_list.py`.  
- Choose your village.  
- Set troop distribution strategies (e.g., send groups of 20 legionnaires first, then 6 Equites Imperatoris after depletion).

> I’m happy with this flow because it hides the underlying complexity, exactly as good code should.

---

## ⚡ (Optional) Alternative Raiding

You can also raid using `oasis_scanning_from_raid_list.py`, which pulls from internal raid lists.  
However, this method is **not actively maintained** and may require small fixes.  
Overall, the scan-based system is more efficient and reliable. 😄


# 🔥 Project Highlights

## API-based Automation (Reverse Engineering Approach)

### `identity_handling/login.py`:
- Loads credentials (`TRAVIAN_EMAIL` and `TRAVIAN_PASSWORD`) from a `.env` file, creating it if missing.
- Logs into Travian using the PKCE OAuth2 authentication flow.
- Retrieves your active avatars and servers using GraphQL.
- Lets you select the server from a menu (auto-selectable if you want).

---

### `oasis_raiding_from_scan_list_main.py` (Main Raiding Automation):

✅ After logging in and selecting your server and village, the script:
1. **Loads your villages** from your identity card (`identity.json`).
2. **Loads the latest full map scan** saved in your local database.
3. **Parses unoccupied oases** only (true "Unoccupied oasis", not wilderness).
4. **Fetches available troops** automatically (no more manual inputs).
5. **Asks you for unit and troops per raid**, or uses your hardcoded defaults.
6. **Raids only oases that are truly empty (no animals)**.
7. **Raids from closest to furthest**, ordered by distance.
8. **Handles the Travian checksum** system for sending legit-looking attacks.
9. **Stops automatically** when you run out of troops.

---

### `full_scan_oasis_analysis.py` (Oasis Mapping):

- **Scans and saves** all unoccupied oases around your village.
- **Sorts oases by distance** for smart farming.
- **Stores clean, reusable JSON datasets** inside `database/unoccupied_oases/`.

---

### `core/travian_api.py`:

- **Wraps Travian API requests**: troops, raids, map data, attacks, farm lists, hero actions.
- Clean, simple, and highly expandable.
- Fully bypasses UI limitations — acts as a lightweight mobile API client.

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

- API_based_automations/
  - oasis_raiding/
    - __pycache__/
    - analysis/
    - database/
      - full_map_scans/
      - identity_card/
      - unoccupied_oases/
    - core/
      - travian_api.py
    - identity_handling/
      - login.py
    - proof_of_concepts/
    - map_scanning_main.py
    - full_scan_oasis_analysis.py
    - oasis_raiding_from_scan_list_main.py
    - oasis_raiding_from_raid_list_main.py
    - requirements.txt
- selenium_UI_based_exploits/
  - gettingCookies.py
  - seleniumTest.py
  - test_TravianVillagesRaidFirefox.py
  - VillageOasisRaidRecording.py
- README.md
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

