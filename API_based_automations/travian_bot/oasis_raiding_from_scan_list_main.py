# oasis_raiding_from_scan_list_main.py

import os
import json
import time
from glob import glob
from random import uniform

from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity
from core.travian_api import TravianAPI
from analysis.number_to_unit_mapping import get_unit_name
from core.database_helpers import load_latest_unoccupied_oases


# === CONFIG ===
BASE_OASIS_FOLDER = "API_based_automations/oasis_raiding/database/unoccupied_oases/"


def main():
    print("[+] Logging in...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Loading villages from identity file...")
    villages = load_villages_from_identity()

    if not villages:
        print("[-] No villages found in identity. Exiting.")
        return

    # Choose village to raid from
    print("\nAvailable villages:")
    for idx, v in enumerate(villages):
        print(f"  [{idx}] {v['village_name']} at ({v['x']},{v['y']})")

    try:
        village_index = int(input("\nSelect the village to raid from (index): ").strip())
    except ValueError:
        print("[-] Invalid village index.")
        return

    if not (0 <= village_index < len(villages)):
        print("[-] Village index out of range.")
        return

    selected_village = villages[village_index]
    village_id = selected_village["village_id"]
    village_x = selected_village["x"]
    village_y = selected_village["y"]
    print(f"[+] Selected village: {selected_village['village_name']} (ID {village_id})")

    # Faction detection
    print("[+] Fetching player info...")
    player_info = api.get_player_info()
    faction_id = player_info.get("faction")  # 1 = Roman, 2 = Teuton, 3 = Gaul
    faction_mapping = {1: "roman", 2: "teuton", 3: "gaul"}
    faction = faction_mapping.get(faction_id, "roman")
    print(f"[+] Detected faction: {faction.title()}")

    # Load latest oasis list
    print("\n[+] Loading unoccupied oases for selected village...")
    village_coords_folder = f"({village_x}_{village_y})"
    oases = load_latest_unoccupied_oases(village_coords_folder)
    if not oases:
        return

    print(f"[+] Found {len(oases)} unoccupied oases. Preparing raids...")

    print("[+] Fetching current troop counts...")
    troops_info = api.get_troops_in_village()
    if not troops_info:
        print("[-] Could not fetch troops. Exiting.")
        return

    print("[+] Current troops in village:")
    for unit_code, amount in troops_info.items():
        unit_name = get_unit_name(unit_code, faction)
        print(f"    {unit_code} ({unit_name}): {amount} units")

    # Ask user for raid setup
    unit_code_for_raid = input("\nEnter unit code for raiding (e.g., u5 for Equites Imperatoris): ").strip()

    available_troops = troops_info.get(unit_code_for_raid, 0)
    if available_troops <= 0:
        print(f"[-] No available troops of type {unit_code_for_raid}. Exiting.")
        return

    try:
        troops_per_raid = int(input("How many troops per raid? ").strip())
    except ValueError:
        print("[-] Invalid number. Exiting.")
        return

    unit_code_for_payload = unit_code_for_raid.replace("u", "t")  # Convert for Travian server

    sent_raids = 0

    for coords, tile in oases.items():
        if available_troops < troops_per_raid:
            print("[!] Not enough troops left to continue.")
            break

        x_str, y_str = coords.split("_")
        x, y = int(x_str), int(y_str)

        animal_count = api.get_oasis_animal_count(x, y)
        if animal_count is None:
            continue

        if animal_count > 0:
            print(f"[-] Skipping oasis at ({x}, {y}) — {animal_count} animals present.")
            continue

        print(f"[+] Launching raid on unoccupied oasis at ({x}, {y})...")
        raid_setup = {unit_code_for_payload: troops_per_raid}

        attack_info = api.prepare_oasis_attack(None, x, y, raid_setup)
        success = api.confirm_oasis_attack(attack_info, x, y, raid_setup, village_id)

        if success:
            print(f"✅ Raid sent to ({x}, {y})")
            sent_raids += 1
            available_troops -= troops_per_raid
        else:
            print(f"❌ Failed to send raid to ({x}, {y})")

        time.sleep(uniform(0.5, 1.2))  # Human-like delay

    print(f"\n[+] Finished sending {sent_raids} raids. Troops remaining: {available_troops}")

if __name__ == "__main__":
    main()
