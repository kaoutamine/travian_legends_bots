from API_based_automations.oasis_raiding.identity_handling.login import login
from travian_api import TravianAPI

# === CONFIG ===
VILLAGE_INDEX = 0  # index of village to use
FARMLIST_NAME = "Close Oasises"  # name of the farm list to use
TROOP_SETUP = {
    "t5": 6  # number of Equites Imperatoris to send
}

def main():
    print("[+] Logging in...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Fetching player info...")
    player_info = api.get_player_info()
    village = player_info["villages"][VILLAGE_INDEX]
    village_id = village["id"]
    print(f"[+] Selected village: {village['name']} (ID {village_id})")

    print(f"[+] Looking for farm list named '{FARMLIST_NAME}'...")
    farm_list = next(
        (f for f in player_info["farmLists"] if f["name"] == FARMLIST_NAME and f["ownerVillage"]["id"] == village_id),
        None
    )
    if not farm_list:
        raise Exception(f"[-] Farm list '{FARMLIST_NAME}' not found for village ID {village_id}.")

    print(f"[+] Fetching targets from farm list '{farm_list['name']}'...")
    list_details = api.get_farm_list_details(farm_list["id"])
    slots = list_details["slots"]

    print(f"[+] Found {len(slots)} targets. Scanning for unprotected oases...")
    for slot in slots:
        target = slot["target"]
        x, y, map_id = target["x"], target["y"], target["mapId"]

        animal_count = api.get_oasis_animal_count(x, y)
        if animal_count > 0:
            print(f"[-] Skipping oasis at ({x}, {y}) — {animal_count} animals present.")
            continue

        print(f"[+] Launching raid on unprotected oasis at ({x}, {y})...")
        attack_info = api.prepare_oasis_attack(map_id, x, y, TROOP_SETUP)
        success = api.confirm_oasis_attack(attack_info, x, y, TROOP_SETUP, village_id)

        if success:
            print(f"✅ Raid sent to ({x}, {y})")
        else:
            print(f"❌ Failed to send raid to ({x}, {y})")

if __name__ == "__main__":
    main()
