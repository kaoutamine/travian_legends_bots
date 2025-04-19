# 🚀 Automate Your Travian Gameplay Like a Pro  
## 🕵️ Stay Fast. Stay Stealthy. Dominate Efficiently.

---

This project **connects directly to Travian’s servers** using clean, fast **API calls** — no browser automation needed.

If you know a little **Python**, can run a few scripts, and don't mind answering some simple **terminal questions**,  
you can fully **automate your early-game oasis raiding in minutes**.

> 🛠 Built by players, for players.  
> 🛡 Looks, acts, and feels like a legit human player.

---

# 🧠 Project Summary

| Feature | Status |
|:---|:---|
| Login via OAuth2 PKCE | ✅ |
| Server and village selection | ✅ |
| Map scanning and analysis | ✅ |
| Oasis raiding automation | ✅ |
| Animal detection and safe attacks | ✅ |
| Travian checksum bypass | ✅ |
| Real-world account ready | ✅ |

---

# 📚 Modules Breakdown

## 🛂 `identity_handling/login.py`
- Secure login using OAuth2 PKCE flow.
- Automatically create `.env` if missing.
- Fetches avatars and servers via GraphQL.
- Saves your identity card locally.

---

## 🛠 `core/travian_api.py`
- Core Travian API abstraction layer.
- Handles sending attacks, scanning villages, reading troops, etc.
- Manages Travian checksum protections.
- Fast, robust, and battle-tested.

---

## 🗺 `map_scanning_main.py`
- Full 25x25 radius map scan around your village.
- Saves a snapshot of all tiles: oases, villages, wilderness.
- Stores map snapshots timestamped.

---

## ⚔️ `oasis_raiding_from_scan_list_main.py`
- Auto raids all unoccupied, undefended oases.
- Sorts by closest first for efficiency.
- Detects animals and skips protected oases.
- Stops automatically when troops run out.

---

## 🧪 `proof_of_concepts/check_sum_attack_breaking_script.py`
- Proof that Travian's checksum can be extracted and reused.
- Allows server-side validated attacks.
- Integrated into `travian_api.py`.

---

## 📂 `database/`
- Stores:
  - Identity card (villages, coordinates, faction).
  - Map scans.
  - Extracted unoccupied oases.
  - Troop mappings (`u1`, `u2`, etc to real unit names).

---


# 📂 Project Structure
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

