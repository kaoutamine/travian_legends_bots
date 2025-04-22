import os
import json
import time
from glob import glob
from random import uniform
import logging

from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity
from core.travian_api import TravianAPI
from analysis.number_to_unit_mapping import get_unit_name
from core.database_helpers import load_latest_unoccupied_oases

# === CONFIG ===
BASE_OASIS_FOLDER = "API_based_automations/oasis_raiding/database/unoccupied_oases/"

class NoTimestampFormatter(logging.Formatter):
    def format(self, record):
        return f"[{record.levelname}] {record.getMessage()}"

console_handler = logging.StreamHandler()
console_handler.setFormatter(NoTimestampFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler]
)


def main():
    logging.info("Logging in...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    logging.info("Loading villages from identity file...")
    villages = load_villages_from_identity()

    if not villages:
        logging.error("No villages found in identity. Exiting.")
        return

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

    logging.info("Fetching player info...")
    player_info = api.get_player_info()
    faction_id = player_info.get("faction")
    faction_mapping = {1: "roman", 2: "teuton", 3: "gaul"}
    faction = faction_mapping.get(faction_id, "roman")
    logging.info(f"Detected faction: {faction.title()}")

    logging.info("Loading unoccupied oases for selected village...")
    village_coords_folder = f"({village_x}_{village_y})"
    oases = load_latest_unoccupied_oases(village_coords_folder)
    if not oases:
        return

    logging.info(f"Found {len(oases)} unoccupied oases. Preparing raids...")

    logging.info("Fetching current troop counts...")
    troops_info = api.get_troops_in_village()
    if not troops_info:
        logging.error("Could not fetch troops. Exiting.")
        return

    logging.info("Current troops in village:")
    for unit_code, amount in troops_info.items():
        unit_name = get_unit_name(unit_code, faction)
        logging.info(f"    {unit_name} ({unit_code}): {amount} units")

    unit_codes_for_raid = input("\nEnter unit codes for raiding (comma-separated, e.g., u5,u2): ").strip().split(",")
    raid_plan = []

    for code in unit_codes_for_raid:
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

    if not raid_plan:
        logging.error("No valid raid plan. Exiting.")
        return

    sent_raids = 0

    for coords, tile in oases.items():
        for unit in raid_plan:
            if unit["available"] >= unit["group_size"]:
                x_str, y_str = coords.split("_")
                x, y = int(x_str), int(y_str)

                animal_count = api.get_oasis_animal_count(x, y)
                if animal_count is None:
                    continue

                if animal_count > 0:
                    logging.warning(f"Skipping oasis at ({x}, {y}) — {animal_count} animals present.")
                    break

                unit_name = get_unit_name(unit['unit_code'], faction)
                logging.info(f"Launching raid on unoccupied oasis at ({x}, {y}) using {unit_name}...")
                raid_setup = {unit["unit_payload_code"]: unit["group_size"]}

                attack_info = api.prepare_oasis_attack(None, x, y, raid_setup)
                success = api.confirm_oasis_attack(attack_info, x, y, raid_setup, village_id)

                if success:
                    logging.info(f"✅ Raid sent to ({x}, {y}) with {unit['group_size']} {unit_name} units")
                    sent_raids += 1
                    unit["available"] -= unit["group_size"]
                else:
                    logging.error(f"❌ Failed to send raid to ({x}, {y}) with {unit['group_size']} {unit_name} units")

                time.sleep(uniform(0.5, 1.2))
                break
        else:
            logging.warning("No more troops available to continue.")
            break

    logging.info(f"\nFinished sending {sent_raids} raids.")
    logging.info("Troops remaining:")
    for unit in raid_plan:
        unit_name = get_unit_name(unit['unit_code'], faction)
        logging.info(f"    {unit_name}: {unit['available']} left")

if __name__ == "__main__":
    main()
