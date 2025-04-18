from login import login
from travian_api import TravianAPI

# === CONFIG ===
TROOP_SETUP = {
    "t5": 6  # 6 Equites Imperatoris
}

def main():
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("\n[+] Fetching your villages and farm lists...")
    player_info = api.get_player_info()
    villages = player_info["villages"]
    farm_lists = player_info["farmLists"]

    print("\nYour villages:")
    for idx, village in enumerate(villages):
        print(f"[{idx}] {village['name']} (ID {village['id']})")

    village_idx = int(input("\nSelect your village: "))
    selected_village = villages[village_idx]
    village_id = selected_village['id']

    print(f"\n[+] Selected village: {selected_village['name']} (ID {village_id})")

    village_farm_lists = [fl for fl in farm_lists if fl["ownerVillage"]["id"] == village_id]

    if not village_farm_lists:
        print("[-] No farm lists found for this village.")
        return

    print("\nFarm Lists belonging to this village:")
    for idx, fl in enumerate(village_farm_lists):
        print(f"[{idx}] {fl['name']}")

    farm_list_idx = int(input("\nSelect the farm list you want to scan: "))
    selected_farm_list = village_farm_lists[farm_list_idx]
    farm_list_id = selected_farm_list['id']

    print(f"\n[+] Scanning farm list: {selected_farm_list['name']}")

    farm_list_details = api.get_farm_list_details(farm_list_id)
    slots = farm_list_details["slots"]

    print(f"\n[+] Found {len(slots)} slots.\n")

    protected = 0
    unprotected = 0

    for idx, slot in enumerate(slots):
        target = slot.get("target")
        if not target:
            continue

        x = target.get("x")
        y = target.get("y")
        map_id = target.get("mapId")
        target_name = target.get("name", "Unnamed Oasis")

        print(f"[{idx}] 🌿 Checking oasis '{target_name}' at ({x}, {y})...", end=" ")

        try:
            animal_count = api.get_oasis_animal_count(x, y)
        except Exception as e:
            print(f"⚠️ Error checking oasis: {e}")
            continue

        if animal_count == 0:
            print(f"🟢 No animals detected ➔ Sending attack...")
            try:
                attack_info = api.prepare_oasis_attack(map_id)
                success = api.confirm_oasis_attack(attack_info, x, y, TROOP_SETUP, village_id)
                if success:
                    print("✅ Attack launched!")
                else:
                    print("❌ Attack failed!")
            except Exception as e:
                print(f"❌ Attack error: {e}")
            unprotected += 1
            break  # Only attack 1 empty oasis for safety
        else:
            print(f"🔴 Oasis protected by {animal_count} animals ➔ Skipping.")
            protected += 1

    print("\n[+] Summary:")
    print(f"🔴 Protected oases: {protected}")
    print(f"🟢 Empty oases attacked: {unprotected}")

if __name__ == "__main__":
    main()
