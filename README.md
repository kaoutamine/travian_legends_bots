The project is divided into two pieces :

## The first is an attempt to connect to Travian the "organic" way with Selenium.
This attempt is for now abandonned. The idea was to use a browser to connect to Travian and then replicate
a specific path using the Selenium plugin (works only on firefox these days) to for example launch the raid lists in Travian.
It worked but ignore it. It's slow and I can't easily generalise it.

## The second is a classic attempt by reverse engineering logins with Burp Suite/Inspect, storing variables and making API requests

### `login.py`:
- Stores your variables in a `.env` file (`TRAVIAN_EMAIL` and `TRAVIAN_PASSWORD`).
- Logs into Travian using the PKCE OAuth2 flow.
- Retrieves your active avatars and the servers they belong to via GraphQL.
- Lets you choose the server you want to log into from a terminal menu.

---

### `main.py` (current working automation):

✅ After logging in and choosing your server and village, the script:
1. **Fetches your villages** and lets you pick one.
2. **Fetches your farm lists** for that village.
3. **Fetches the targets** inside the chosen farm list (typically nearby oases).
4. **Scans each target** for animal defenders.
5. **Sends troops** (e.g., 6 Equites Imperatoris) **only to unprotected oases** (animal count = 0).
6. **Successfully handles the Travian checksum protection** required to launch raids (simulating legit player actions).

---

### `check_sum_attack_breaking_script.py` (Proof of Concept):
- **Extracts and uses the Travian checksum protection** when sending manual troop attacks.
- **Successfully replicates a real human launching an attack**, passing all server validations.

✅ **This logic is now fully integrated into the main raiding automation!**

---

### Next Steps:

- Modularize key functions inside `TravianAPI` for reuse (already started with `prepare_oasis_attack` and `confirm_oasis_attack`).
- Create a **script to launch raid lists** automatically (standard village raids, not just oasis checks).
- Create a **smart hero oasis raider**, which:
  - Checks hero health and equipment.
  - Picks appropriately weak oases automatically based on oasis defenders.
- Build a **systematic oasis mapping script**:
  - Perform a **grid search** around your village coordinates.
  - Auto-build your own farm list by discovering and recording nearby empty oases.

---

✅ Project is fully API-driven (no browser dependency).  
✅ Script is fast, lightweight, and server-compatible.
