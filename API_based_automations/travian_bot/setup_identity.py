import os
import sys
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from identity_handling.login import login
from identity_handling.faction_utils import get_faction_name

def verify_faction(tribe_id: int) -> tuple[int, str]:
    """Ask user to verify or correct the faction name."""
    try:
        current_faction = get_faction_name(tribe_id)
    except ValueError:
        current_faction = "unknown"
    
    print(f"\nCurrent faction mapping: {tribe_id} -> {current_faction}")
    print("Available factions:")
    print("1. Roman")
    print("2. Teuton")
    print("3. Gaul")
    print("6. Egyptian")
    print("7. Hun")
    print("0. Other (please specify)")
    
    while True:
        try:
            choice = input("\nIs this correct? (y/n): ").lower().strip()
            if choice == 'y':
                return tribe_id, current_faction
            elif choice == 'n':
                new_choice = input("Enter the correct faction number (1-7) or 0 for other: ").strip()
                if new_choice == '0':
                    custom_faction = input("Enter the custom faction name: ").strip().lower()
                    return 0, custom_faction  # Use 0 as tribe_id for custom factions
                else:
                    new_id = int(new_choice)
                    return new_id, get_faction_name(new_id)
            else:
                print("Please enter 'y' or 'n'")
        except ValueError:
            print("Invalid input. Please try again.")

def fetch_villages_with_coordinates(session, server_url):
    """Fetch own villages (ID + name), ask user to input (x, y) manually."""
    print("[+] Fetching your villages from Travian...")

    payload = {
        "query": """
            query {
                ownPlayer {
                    currentVillageId
                    villages {
                        id
                        sortIndex
                        name
                        tribeId
                        hasHarbour
                    }
                    farmLists {
                        id
                        name
                        ownerVillage {
                            id
                        }
                    }
                }
            }
        """
    }

    response = session.post(f"{server_url}/api/v1/graphql", json=payload)
    response.raise_for_status()

    response_json = response.json()
    print("[DEBUG] GraphQL Response:", response_json)

    if "errors" in response_json:
        print("\n❌ GraphQL Error:", response_json["errors"])
        raise Exception("GraphQL query failed. Check if you are properly logged in.")

    own_player = response_json.get("data", {}).get("ownPlayer")
    if own_player is None:
        raise Exception("❌ 'ownPlayer' missing in response. Something went wrong.")

    villages_info = own_player["villages"]
    print(f"[+] Found {len(villages_info)} villages.")

    # Get player's tribe/faction first (using first village's tribeId as reference)
    if villages_info:
        tribe_id = villages_info[0]["tribeId"]
        print("\n[👤] Let's verify your tribe/faction first:")
        player_tribe_id, player_faction = verify_faction(tribe_id)
        print(f"✅ Your faction is set to: {player_faction.title()}")
    else:
        raise Exception("❌ No villages found!")

    final_villages = []

    for village in villages_info:
        village_id = village["id"]
        village_name = village["name"]
        print(f"\n[🏡] Village '{village_name}' (ID {village_id})")

        while True:
            try:
                coords_input = input("Enter coordinates for this village (format: x y): ").strip().split()
                if len(coords_input) != 2:
                    raise ValueError
                x, y = map(int, coords_input)
                break
            except ValueError:
                print("❌ Invalid input. Please enter two integers separated by a space.")

        final_villages.append({
            "village_name": village_name,
            "village_id": village_id,
            "x": x,
            "y": y
        })

    print(f"\n✅ Finished collecting coordinates for {len(final_villages)} villages.")
    return final_villages, player_tribe_id, player_faction

def save_identity(session, server_url):
    """Fetch village info and save it into database/identity.json."""
    villages, tribe_id, faction = fetch_villages_with_coordinates(session, server_url)

    identity_data = {
        "travian_identity": {
            "created_at": "2025-04-22T00:00:00Z",  # (Optional) You can later make it dynamic with datetime.now()
            "tribe_id": tribe_id,
            "faction": faction,
            "servers": [
                {
                    "server_name": server_url,
                    "server_url": server_url,
                    "villages": villages
                }
            ]
        }
    }

    # Make sure database folder exists
    database_folder = os.path.join("database")
    os.makedirs(database_folder, exist_ok=True)
    identity_file = os.path.join(database_folder, "identity.json")

    with open(identity_file, "w", encoding="utf-8") as f:
        json.dump(identity_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Identity saved successfully at {identity_file}")

def main():
    print("[+] Setting up your Travian identity...")
    print("This script will:")
    print("1. Log you into your Travian account")
    print("2. Verify your tribe/faction")
    print("3. Get coordinates for each of your villages")
    print("4. Save all this information for use by other scripts")
    print("\nPress Enter to continue...")
    input()

    session, server_url = login()
    save_identity(session, server_url)

if __name__ == "__main__":
    main() 