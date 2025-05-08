import os
import json
import logging
from random import uniform

from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity
from core.travian_api import TravianAPI
from analysis.number_to_unit_mapping import get_unit_name
from core.database_helpers import load_latest_unoccupied_oases
from core.database_raid_config import load_saved_raid_plan, save_raid_plan
from core.raid_runner import run_raid_batch
from core.hero_runner import try_send_hero_to_oasis  # ✅ Hero logic
from identity_handling.faction_utils import get_faction_name

class NoTimestampFormatter(logging.Formatter):
    def format(self, record):
        return f"[{record.levelname}] {record.getMessage()}"

console_handler = logging.StreamHandler()
console_handler.setFormatter(NoTimestampFormatter())
logging.basicConfig(level=logging.INFO, handlers=[console_handler])

def run_raid_planner(
    api,
    server_url,
    reuse_saved=True,
    selected_village_index=None,
    units_to_use=None,
    enable_hero_raiding=True,
    interactive=False
):

    saved_data = load_saved_raid_plan()

    if not saved_data:
        logging.error("❌ No saved raid plan found. You must run it once interactively to save one.")
        return

    villages = load_villages_from_identity()
    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

    if reuse_saved and saved_data["server"] == server_url:
        village_index = saved_data["village_index"]
        logging.info(f"✅ Using saved village index: {village_index}")
    else:
        if selected_village_index is None:
            logging.error("❌ No village index provided and not using saved config.")
            return
        village_index = selected_village_index

    selected_village = villages[village_index]
    village_id = selected_village["village_id"]
    village_x = selected_village["x"]
    village_y = selected_village["y"]
    logging.info(f"Selected village: {selected_village['village_name']} (ID {village_id})")

    # Load faction from identity.json
    try:
        with open("database/identity.json", "r", encoding="utf-8") as f:
            identity = json.load(f)
            tribe_id = identity["travian_identity"]["tribe_id"]
            faction = get_faction_name(tribe_id)
            logging.info(f"Detected faction: {faction.title()}")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading identity: {e}")
        return

    troops_info = api.get_troops_in_village()
    if not troops_info:
        logging.error("Could not fetch troops. Exiting.")
        return

    logging.info("Current troops in village:")
    for unit_code, amount in troops_info.items():
        unit_name = get_unit_name(unit_code, faction)
        logging.info(f"    {unit_name} ({unit_code}): {amount} units")

    # Use saved raid plan
    raid_plan = saved_data["raid_plan"]
    for unit in raid_plan:
        unit["available"] = troops_info.get(unit["unit_code"], 0)

    oases = load_latest_unoccupied_oases(f"({village_x}_{village_y})")

    # --- HERO LOGIC START ---
    hero_available = troops_info.get("uhero", 0) >= 1
    hero_sent = False

    if enable_hero_raiding and hero_available:
        for coord_key, oasis_data in oases.items():
            x_str, y_str = coord_key.split("_")
            oasis = {"x": int(x_str), "y": int(y_str)}
            if try_send_hero_to_oasis(api, selected_village, oasis):
                hero_sent = True
                break
    # --- HERO LOGIC END ---

    run_raid_batch(api, saved_data, faction, village_id, oases)

    # --- HERO RESULT REPORT ---
    print("\n--- Hero Raid Summary ---")
    if not enable_hero_raiding:
        print("Hero raiding was disabled.")
    elif not hero_available:
        print("Hero was not available.")
    elif hero_sent:
        print("✅ Hero was sent on a raid.")
    else:
        print("⚠️ Hero was available but no suitable oasis was found.")

if __name__ == "__main__":
    run_raid_planner()
