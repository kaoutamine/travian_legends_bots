import random
import time
from login import login
from travian_api import TravianAPI
from database.identity_card import load_identity_card

# === CONFIG ===
VILLAGE_INDEX = 0  # Choose which village to scan around
SCAN_RADIUS = 20   # How many tiles around the village (in each direction)

def main():
    print("[+] Logging in...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    print("[+] Fetching player info...")
    player_info = api.get_player_info()
    villages = player_info["villages"]

    selected_village = villages[VILLAGE_INDEX]
    village_id = selected_village["id"]
    print(f"[+] Selected village: {selected_village['name']} (ID {village_id})")

    # Load identity card
    identity_card = load_identity_card()
    server_info = identity_card.get(server_url)
    if not server_info:
        raise Exception(f"[-] No identity card entry for server {server_url}")

    # Get the village with coordinates
    village_data = next((v for v in server_info["villages"] if v["id"] == village_id), None)
    if not village_data:
        raise Exception(f"[-] No coordinate info for village ID {village_id} in identity card.")

    center_x, center_y = village_data["x"], village_data["y"]
    print(f"[+] Using center coordinates: ({center_x}, {center_y})")

    print("[+] Starting map scan...")

    scanned_tiles = []

    for dx in range(-SCAN_RADIUS, SCAN_RADIUS + 1):
        for dy in range(-SCAN_RADIUS, SCAN_RADIUS + 1):
            x, y = center_x + dx, center_y + dy

            try:
                tile_html = api.get_tile_html(x, y)
                scanned_tiles.append({
                    "x": x,
                    "y": y,
                    "html": tile_html
                })
                print(f"[+] Scanned tile at ({x}, {y})")
            except Exception as e:
                print(f"[!] Failed to scan ({x}, {y}): {str(e)}")

            # Add a small random human-like delay
            time.sleep(random.uniform(0.5, 1.0))

    print(f"[+] Scan complete! Total tiles scanned: {len(scanned_tiles)}")

    # Save the result
    import json
    with open("scanned_tiles.json", "w") as f:
        json.dump(scanned_tiles, f, indent=2)
    print("[+] Saved scanned tiles to scanned_tiles.json")

if __name__ == "__main__":
    main()
