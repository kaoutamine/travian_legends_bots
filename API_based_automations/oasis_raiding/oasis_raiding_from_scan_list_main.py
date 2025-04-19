from identity_handling.login import login
from travian_api import TravianAPI
import os
import json
from glob import glob
from random import uniform
import time

# === CONFIG ===
VILLAGE_INDEX = 0  # index of village to use
TROOP_SETUP = {
    "t5": 6  # number of Equites Imperatoris to send
}
OASIS_FOLDER = "API_based_automations/oasis_raiding/database/unoccupied_oases/"

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
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Fetching player info...")
    player_info = api.get_player_info()
    village = player_info["villages"][VILLAGE_INDEX]
    village_id = village["id"]
    print(f"[+] Selected village: {village['name']} (ID {village_id})")

    print("[+] Loading unoccupied oases from latest map scan...")
    oases = load_latest_unoccupied_oases()
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
        print(f"    {unit_code}: {amount} units")

    # You can now see all available units
    print("\n[+] Reminder of unit code for Romans:")
    print("    u1: Legionnaire")
    print("    u2: Praetorian")
    print("    u3: Imperian")
    print("    u4: Equites Legati")
    print("    u5: Equites Imperatoris")
    print("    u6: Equites Caesaris")
    print("    ...and more depending on your faction.")

    # Now specifically get Equites Imperatoris
    available_troops = troops_info.get("u5", 0)
    print(f"\n[+] You have {available_troops} Equites Imperatoris available.")

    troops_per_raid = int(input("How many troops per raid? "))


    sent_raids = 0

    for coords, tile in oases.items():
        if available_troops < troops_per_raid:
            print("[!] Not enough troops left to continue.")
            break

        x_str, y_str = coords.split("_")
        x, y = int(x_str), int(y_str)

        # Check for animal defenders before launching
        animal_count = api.get_oasis_animal_count(x, y)
        if animal_count > 0:
            print(f"[-] Skipping oasis at ({x}, {y}) — {animal_count} animals present.")
            continue

        print(f"[+] Launching raid on unoccupied oasis at ({x}, {y})...")
        attack_info = api.prepare_oasis_attack(None, x, y, TROOP_SETUP)
        success = api.confirm_oasis_attack(attack_info, x, y, TROOP_SETUP, village_id)

        if success:
            print(f"✅ Raid sent to ({x}, {y})")
            sent_raids += 1
            available_troops -= troops_per_raid
        else:
            print(f"❌ Failed to send raid to ({x}, {y})")

        time.sleep(uniform(0.5, 1.2))  # Human-like delay

    print(f"[+] Finished sending {sent_raids} raids. Troops remaining: {available_troops}")

if __name__ == "__main__":
    main()
