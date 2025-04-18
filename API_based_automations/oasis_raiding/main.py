# main.py

from login import login
from farm_list import fetch_farm_list, parse_farm_list

LIST_ID = 761  # Change this to your real farm list ID

def main():
    # Login to Travian
    session, server_url = login()
    print(f"[+] Connected to {server_url}")
    
    # Fetch your farm list
    raw_farm_list_data = fetch_farm_list(session, LIST_ID)
    farms = parse_farm_list(raw_farm_list_data)

    # Example: Display all farms
    for farm in farms:
        print(f"Target {farm['target_name']} at ({farm['x']},{farm['y']}): {farm['total_loot']} loot")
        if farm['total_loot'] < 10:
            print("  -> Not worth raiding again.")
        else:
            print("  -> Good loot! Should re-attack soon.")

if __name__ == "__main__":
    main()
