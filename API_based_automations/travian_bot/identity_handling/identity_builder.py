import os
import json
from identity_handling.faction_utils import get_faction_name

# === LOCATION CONSTANTS ===
DATABASE_FOLDER = os.path.join(os.path.dirname(__file__), "..", "database")
IDENTITY_FILE = os.path.join(DATABASE_FOLDER, "identity.json")

# Make sure database folder exists
os.makedirs(DATABASE_FOLDER, exist_ok=True)

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

    final_villages = []

    for village in villages_info:
        village_id = village["id"]
        village_name = village["name"]
        tribe_id = village["tribeId"]
        faction_name = get_faction_name(tribe_id)
        print(f"\n[🏡] Village '{village_name}' (ID {village_id}) - {faction_name.title()}")

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
            "y": y,
            "tribe_id": tribe_id,
            "faction": faction_name
        })

    print(f"\n✅ Finished collecting coordinates for {len(final_villages)} villages.")
    return final_villages

def save_identity(session, server_url):
    """Fetch village info and save it into database/identity.json."""
    villages = fetch_villages_with_coordinates(session, server_url)

    identity_data = {
        "travian_identity": {
            "created_at": "2025-04-22T00:00:00Z",  # (Optional) You can later make it dynamic with datetime.now()
            "servers": [
                {
                    "server_name": server_url,
                    "server_url": server_url,
                    "villages": villages
                }
            ]
        }
    }

    with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(identity_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Identity saved successfully at {IDENTITY_FILE}")
