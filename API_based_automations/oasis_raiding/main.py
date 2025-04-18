# main.py

from login import login
from farm_list import fetch_farm_lists_with_ids, fetch_farm_list, parse_farm_list

def main():
    # Login to Travian
    session, server_url = login()
    print(f"[+] Connected to {server_url}")

    # 🚀 Ask user for their farming village ID
    village_id = int(input("Enter your farming village ID (you can find it from your village list): "))

    # 🚀 Fetch available farm lists for the village
    farm_lists = fetch_farm_lists_with_ids(session, village_id)
    
    if not farm_lists:
        print("[-] No farm lists found for this village.")
        return

    print("\nAvailable Farm Lists:")
    for idx, farm_list in enumerate(farm_lists):
        print(f"[{idx}] {farm_list['name']} (ID: {farm_list['id']}, Slots: {farm_list['slots_amount']})")

    # 🚀 User selects a farm list
    selected_idx = int(input("\nSelect the farm list number you want to use: "))
    selected_farm_list = farm_lists[selected_idx]

    print(f"\n[+] Using farm list: {selected_farm_list['name']} (ID: {selected_farm_list['id']})")

    # 🚀 Fetch the farm list content
    raw_farm_list_data = fetch_farm_list(session, selected_farm_list['id'])
    farms = parse_farm_list(raw_farm_list_data)

    # 🚀 Display all farms inside
    print("\nFarm list content:")
    for farm in farms:
        print(f"Target {farm['target_name']} at ({farm['x']},{farm['y']}): {farm['total_loot']} loot")
        if farm['total_loot'] < 10:
            print("  -> Not worth raiding again.")
        else:
            print("  -> Good loot! Should re-attack soon.")

if __name__ == "__main__":
    main()
