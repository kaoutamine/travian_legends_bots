# main.py

from login import login
from farm_list import (
    fetch_villages_and_farm_lists,
    fetch_farm_lists_with_ids,
    fetch_farm_list,
    parse_farm_list
)

def main():
    # Step 1: Login
    session, server_url = login()
    print(f"[+] Connected to {server_url}")

    # Step 2: Fetch all villages and farm lists
    player_data = fetch_villages_and_farm_lists(session)
    villages = player_data["villages"]

    # Step 3: Display available villages
    print("\nAvailable Villages:")
    for idx, village in enumerate(villages):
        print(f"[{idx}] {village['name']} (ID: {village['id']})")

    # Step 4: Let user choose a village
    selected_village_idx = int(input("\nSelect the village you want to farm from: "))
    selected_village = villages[selected_village_idx]
    village_id = selected_village["id"]

    print(f"\n[+] Selected village: {selected_village['name']} (ID: {village_id})")

    # Step 5: Fetch farm lists for that village
    farm_lists = fetch_farm_lists_with_ids(session, village_id)

    if not farm_lists:
        print("[-] No farm lists found for this village.")
        return

    # Step 6: Display available farm lists
    print("\nAvailable Farm Lists:")
    for idx, farm_list in enumerate(farm_lists):
        print(f"[{idx}] {farm_list['name']} (List ID: {farm_list['id']}, Slots: {farm_list['slots_amount']})")

    # Step 7: Let user choose a farm list
    selected_farm_list_idx = int(input("\nSelect the farm list you want to use: "))
    selected_farm_list = farm_lists[selected_farm_list_idx]
    farm_list_id = selected_farm_list["id"]

    print(f"\n[+] Selected farm list: {selected_farm_list['name']} (List ID: {farm_list_id})")

    # Step 8: Fetch and parse the farm list content
    raw_farm_list_data = fetch_farm_list(session, farm_list_id)
    farms = parse_farm_list(raw_farm_list_data)

    # Step 9: Display parsed farm targets
    print("\nFarm List Content:")
    for farm in farms:
        print(f"Target: {farm['target_name']} ({farm['x']}, {farm['y']})")
        print(f"  Type: {farm['type']}")
        print(f"  Population: {farm['population']}")
        print(f"  Distance: {farm['distance']:.2f}")
        print(f"  Total Loot Last Raid: {farm['total_loot']}")
        print(f"  Next Attack Possible: {farm['next_attack_at']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
