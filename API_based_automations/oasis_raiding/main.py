# main.py

from login import login
from travian_api import TravianAPI

def main():
    # Step 1: Login
    session, server_url = login()
    travian = TravianAPI(session, server_url)

    # Step 2: Fetch all villages and farm lists
    player_data = travian.fetch_villages_and_farm_lists()

    villages = player_data["villages"]
    farm_lists = player_data["farmLists"]

    print("Available Villages:")
    for i, village in enumerate(villages):
        print(f"[{i}] {village['name']} (ID: {village['id']})")

    print("\nAvailable Farm Lists:")
    for i, fl in enumerate(farm_lists):
        print(f"[{i}] {fl['name']} (Owner Village ID: {fl['ownerVillage']['id']})")

    selected_index = int(input("\nSelect a Farm List to load (index): "))
    selected_farm_list = farm_lists[selected_index]

    farm_list_details = travian.fetch_farm_list_details(selected_farm_list["id"])
    farms = travian.parse_farm_list_slots(farm_list_details)

    print("\nFarms in this list:")
    for farm in farms:
        print(f"{farm['type']}: {farm['target_name']} at ({farm['x']},{farm['y']}) - Loot: {farm['total_loot']}")

if __name__ == "__main__":
    main()
