import os
import json

# === LOCATION CONSTANTS ===
DATABASE_FOLDER = os.path.join(os.path.dirname(__file__), "..", "database")
IDENTITY_FILE = os.path.join(DATABASE_FOLDER, "identity.json")
ENTITY_FILE = os.path.join(DATABASE_FOLDER, "entities.json")

# Make sure database folder exists
os.makedirs(DATABASE_FOLDER, exist_ok=True)

def load_entities():
    if not os.path.exists(ENTITY_FILE):
        return {}
    with open(ENTITY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_entities(entities):
    with open(ENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)

# --- NEW: Fetch villages and save identity ---
def fetch_villages_with_coordinates(session, server_url):
    """Fetch own villages, try to get coordinates, ask user if missing."""
    # Step 1: Fetch player villages
    payload = {
        "query": """
            query {
                ownPlayer {
                    villages {
                        id
                        name
                    }
                }
            """
    }
    response = session.post(f"{server_url}/api/v1/graphql", json=payload)
    response.raise_for_status()
    villages_info = response.json()["data"]["ownPlayer"]["villages"]

    # Step 2: Try fetching map data for coordinates
    try:
        payload_map = {
            "query": """
                query {
                    map {
                        villages {
                            id
                            x
                            y
                        }
                    }
                """
        }
        response_map = session.post(f"{server_url}/api/v1/graphql", json=payload_map)
        response_map.raise_for_status()
        map_villages = response_map.json()["data"]["map"]["villages"]
        id_to_coords = {v["id"]: (v["x"], v["y"]) for v in map_villages}
    except Exception:
        id_to_coords = {}

    # Step 3: Assemble final village list
    final_villages = []
    for village in villages_info:
        village_id = village["id"]
        village_name = village["name"]
        coords = id_to_coords.get(village_id)

        if coords is None:
            print(f"\n[!] Missing coordinates for village '{village_name}' (ID {village_id})")
            while True:
                try:
                    coords_input = input("Enter coordinates (format: x y): ").strip().split()
                    if len(coords_input) != 2:
                        raise ValueError
                    x, y = map(int, coords_input)
                    break
                except ValueError:
                    print("[-] Invalid input. Please enter two integers separated by a space.")
        else:
            x, y = coords

        final_villages.append({
            "village_name": village_name,
            "village_id": village_id,
            "x": x,
            "y": y
        })

    return final_villages

def save_identity(session, server_url):
    """Fetch village info and save it into database/identity.json."""
    villages = fetch_villages_with_coordinates(session, server_url)

    identity_data = {
        "travian_identity": {
            "created_at": "2025-04-22T00:00:00Z",  # you could make this dynamic later
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
        json.dump(identity_data, f, indent=2)

    print(f"\n✅ Identity saved successfully at {IDENTITY_FILE}")
