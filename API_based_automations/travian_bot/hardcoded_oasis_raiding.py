from identity_handling.login import login
from core.travian_api import TravianAPI
import os
import json
from glob import glob
from random import uniform
import time
from database.number_to_unit_mapping import get_unit_name

# === CONFIG ===
VILLAGE_INDEX = 0  # Always pick first village
OASIS_FOLDER = "API_based_automations/oasis_raiding/database/unoccupied_oases/"

RAID_PRIORITY = [
    ("u1", 20),  # Legionnaires
    ("u5", 6)    # Equites Imperatoris
]

HERO_SEND_MIN = 4  # Minimum animals to send hero
HERO_SEND_MAX = 7  # Maximum animals to send hero

def load_latest_unoccupied_oases():
    scan_files = glob(os.path.join(OASIS_FOLDER, "*.json"))
    if not scan_files:
        print("[-] No unoccupied oases scan found.")
        return None

    latest_file = max(scan_files, key=os.path.getmtime)
    print(f"[+] Using latest unoccupied oases file: {os.path.basename(latest_file)}")

    with open(latest_file, "r") as f:
        oases = json.load(f)

    return oases

def main():
    print("[+] Logging in...")
    session, server_url = login(server_selection=0)
    api = TravianAPI(session, server_url)

    print("[+] Fetching player info...")
    player_info = api.get_player_info()
    village = player_info["villages"][VILLAGE_INDEX]
    village_id = village["id"]
    print(f"[+] Selected village: {village['name']} (ID {village_id})")

    faction_id = player_info.get("faction")
    faction_mapping = {1: "roman", 2: "teuton", 3: "gaul"}
    faction = faction_mapping.get(faction_id, "roman")
    print(f"[+] Detected faction: {faction.title()}")

    print("[+] Loading unoccupied oases from latest map scan...")
    oases = load_latest_unoccupied_oases()
    if not oases:
        return

    oases_list = list(oases.items())  # list of (coords, tile)

    print(f"[+] Found {len(oases_list)} unoccupied oases. Preparing raids...")

    print("[+] Fetching current troop counts...")
    troops_info = api.get_troops_in_village()

    if not troops_info:
        print("[-] Could not fetch troops. Exiting.")
        return

    total_sent_raids = 0
    hero_sent = 0

    # Pre-check if we have a hero alive
    hero_available = troops_info.get("hero", 0) > 0
    if hero_available:
        print("[+] Hero is available for dispatch.")

    for unit_code, troops_per_raid in RAID_PRIORITY:
        available_troops = troops_info.get(unit_code, 0)
        if available_troops <= 0:
            print(f"[-] No available {get_unit_name(unit_code, faction)}. Skipping.")
            continue

        print(f"[+] Preparing {get_unit_name(unit_code, faction)} raids ({available_troops} available)...")
        unit_code_for_payload = unit_code.replace("u", "t")

        while available_troops >= troops_per_raid and oases_list:
            coords, tile = oases_list.pop(0)
            x_str, y_str = coords.split("_")
            x, y = int(x_str), int(y_str)

            animal_count = api.get_oasis_animal_count(x, y)
            if animal_count is None:
                continue

            if HERO_SEND_MIN <= animal_count <= HERO_SEND_MAX and hero_available:
                # Send hero only!
                print(f"[🏹] Sending HERO to oasis at ({x}, {y}) with {animal_count} animals.")
                raid_setup = {"hero": 1}
                attack_info = api.prepare_oasis_attack(None, x, y, raid_setup)
                success = api.confirm_oasis_attack(attack_info, x, y, raid_setup, village_id)

                if success:
                    print(f"✅ Hero dispatched to ({x}, {y})")
                    hero_sent += 1
                    hero_available = False  # Hero is gone until he returns
                else:
                    print(f"❌ Failed to send hero to ({x}, {y})")
                time.sleep(uniform(0.5, 1.2))
                continue  # Do not continue normal raiding after hero sends

            if animal_count > 0:
                print(f"[-] Skipping oasis at ({x}, {y}) — {animal_count} animals present.")
                continue

            print(f"[+] Launching raid with {troops_per_raid} {get_unit_name(unit_code, faction)} at ({x}, {y})...")
            raid_setup = {unit_code_for_payload: troops_per_raid}

            attack_info = api.prepare_oasis_attack(None, x, y, raid_setup)
            success = api.confirm_oasis_attack(attack_info, x, y, raid_setup, village_id)

            if success:
                print(f"✅ Raid sent to ({x}, {y})")
                available_troops -= troops_per_raid
                total_sent_raids += 1
            else:
                print(f"❌ Failed to send raid to ({x}, {y})")

            time.sleep(uniform(0.5, 1.2))  # Human-like delay

    print(f"[+] Finished sending {total_sent_raids} raids and {hero_sent} hero attack(s).")

if __name__ == "__main__":
    main()
