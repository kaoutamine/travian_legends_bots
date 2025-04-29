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

class NoTimestampFormatter(logging.Formatter):
    def format(self, record):
        return f"[{record.levelname}] {record.getMessage()}"

console_handler = logging.StreamHandler()
console_handler.setFormatter(NoTimestampFormatter())
logging.basicConfig(level=logging.INFO, handlers=[console_handler])

def main():
    saved_data = load_saved_raid_plan()

    reuse_saved = False
    if saved_data:
        print("\n📌 Found saved raid config:")
        print(f"   Server: {saved_data['server']}")
        print(f"   Village index: {saved_data['village_index']}")
        print(f"   Units: {[unit['unit_code'] for unit in saved_data['raid_plan']]}")
        print(f"   Units: {[unit['group_size'] for unit in saved_data['raid_plan']]}")
        reuse_saved = input("\nDo you want to reuse this config? [Y/n]: ").strip().lower() in ("", "y", "yes")

    session, server_url = login()
    api = TravianAPI(session, server_url)

    villages = load_villages_from_identity()
    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

    if reuse_saved and saved_data["server"] == server_url:
        village_index = saved_data["village_index"]
        logging.info(f"✅ Using saved village index: {village_index}")
    else:
        logging.info("Available villages:")
        for idx, v in enumerate(villages):
            logging.info(f"  [{idx}] {v['village_name']} at ({v['x']},{v['y']})")
        try:
            village_index = int(input("\nSelect the village to raid from (index): ").strip())
        except ValueError:
            logging.error("Invalid village index.")
            return

    if not (0 <= village_index < len(villages)):
        logging.error("Village index out of range.")
        return

    selected_village = villages[village_index]
    village_id = selected_village["village_id"]
    village_x = selected_village["x"]
    village_y = selected_village["y"]
    logging.info(f"Selected village: {selected_village['village_name']} (ID {village_id})")

    player_info = api.get_player_info()
    faction_id = player_info.get("faction")
    faction_mapping = {1: "roman", 2: "teuton", 3: "gaul"}
    faction = faction_mapping.get(faction_id, "roman")
    logging.info(f"Detected faction: {faction.title()}")

    troops_info = api.get_troops_in_village()
    if not troops_info:
        logging.error("Could not fetch troops. Exiting.")
        return

    logging.info("Current troops in village:")
    for unit_code, amount in troops_info.items():
        unit_name = get_unit_name(unit_code, faction)
        logging.info(f"    {unit_name} ({unit_code}): {amount} units")

    raid_plan = []
    if reuse_saved:
        raid_plan = saved_data["raid_plan"]
        for unit in raid_plan:
            unit["available"] = troops_info.get(unit["unit_code"], 0)
    else:
        unit_codes = input("\nEnter unit codes for raiding (comma-separated, e.g., u1,u5): ").strip().split(",")
        for code in unit_codes:
            code = code.strip()
            available = troops_info.get(code, 0)
            if available <= 0:
                logging.warning(f"No available troops of type {code}. Skipping.")
                continue

            unit_name = get_unit_name(code, faction)
            try:
                group_size = int(input(f"How many {unit_name} per raid? (available: {available}): ").strip())
            except ValueError:
                logging.warning(f"Invalid number for {code}. Skipping.")
                continue

            raid_plan.append({
                "unit_code": code,
                "unit_payload_code": code.replace("u", "t"),
                "group_size": group_size,
                "available": available
            })

        save_raid_plan(server_url, village_index, [
            {k: unit[k] for k in ["unit_code", "unit_payload_code", "group_size"]}
            for unit in raid_plan
        ])

    oases = load_latest_unoccupied_oases(f"({village_x}_{village_y})")

    # --- HERO LOGIC START ---
    hero_available = troops_info.get("uhero", 0) >= 1
    hero_sent = False
    hero_raiding_enabled = input("\n🦸 Enable hero raiding? [Y/n]: ").strip().lower() in ("", "y", "yes")

    if hero_raiding_enabled and hero_available:
        for coord_key, oasis_data in oases.items():
            x_str, y_str = coord_key.split("_")
            oasis = {"x": int(x_str), "y": int(y_str)}
            if try_send_hero_to_oasis(api, selected_village, oasis):
                hero_sent = True
                break

    # --- HERO LOGIC END ---

    run_raid_batch(api, raid_plan, faction, village_id, oases)

    # --- HERO RESULT REPORT ---
    print("\n--- Hero Raid Summary ---")
    if not hero_raiding_enabled:
        print("Hero raiding was disabled.")
    elif not hero_available:
        print("Hero was not available.")
    elif hero_sent:
        print("✅ Hero was sent on a raid.")
    else:
        print("⚠️ Hero was available but no suitable oasis was found.")

if __name__ == "__main__":
    main()
