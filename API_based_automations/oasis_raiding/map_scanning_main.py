import random
import time
import json
from login import login
from travian_api import TravianAPI
from bs4 import BeautifulSoup

# === Tile Class ===
class Tile:
    def __init__(self, x, y, map_id, tile_type, bonus=None, troop_info=None, player_info=None):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.tile_type = tile_type
        self.bonus = bonus
        self.troop_info = troop_info
        self.player_info = player_info

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "mapId": self.map_id,
            "tileType": self.tile_type,
            "bonus": self.bonus,
            "troopInfo": self.troop_info,
            "playerInfo": self.player_info
        }

# === Helper to parse tile ===
def parse_html_to_tile(html, x, y):
    soup = BeautifulSoup(html, "html.parser")
    tile_details = soup.find("div", id="tileDetails")
    
    if tile_details and "oasis" in tile_details.get("class", []):
        tile_type = "oasis"
        bonus = {}
        troop_info = []

        bonus_table = soup.find("table", id="distribution")
        if bonus_table:
            for tr in bonus_table.find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    resource = cells[2].text.strip()
                    percentage = cells[1].text.strip()
                    bonus[resource] = percentage

        troop_table = soup.find("table", id="troop_info")
        if troop_table:
            for row in troop_table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 3:
                    unit_name = cols[2].text.strip()
                    try:
                        unit_count = int(cols[1].text.strip())
                    except:
                        unit_count = 0
                    troop_info.append({"unit": unit_name, "count": unit_count})

        return Tile(x, y, None, tile_type, bonus, troop_info, None)

    # Assume village otherwise (later can refine more)
    return Tile(x, y, None, "unknown")

# === Scan area ===
def scan_area(api, center_x, center_y, radius):
    tiles = []
    total = (radius * 2 + 1) ** 2
    scanned = 0

    print(f"[+] Starting map scan around ({center_x}, {center_y}), radius {radius} tiles...")

    for dx in range(-radius, radius+1):
        for dy in range(-radius, radius+1):
            x, y = center_x + dx, center_y + dy

            print(f"[*] Looking at tile ({x}, {y})...")

            try:
                html = api.get_tile_html(x, y)
                tile = parse_html_to_tile(html, x, y)
                tiles.append(tile)

                scanned += 1
                if scanned % 10 == 0:
                    print(f"[+] {scanned}/{total} tiles scanned...")
            except Exception as e:
                print(f"[!] Oops, failed to scan ({x},{y}): {e}")
                print("[~] Taking a short break before retrying...")
                time.sleep(random.uniform(1.0, 2.5))  # Bigger pause if error
                continue

            time.sleep(random.uniform(0.4, 0.8))  # Slight human-like randomness between scans

    print(f"[+] Finished scanning {len(tiles)} tiles.")
    return tiles

# === Save tiles ===
def save_tiles_to_json(tiles, filename="tiles_dump.json"):
    data = [tile.to_dict() for tile in tiles]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[+] Tiles data saved to {filename}")

# === Main ===
def main():
    print("[+] Logging into Travian...")
    session, server_url = login()
    api = TravianAPI(session, server_url)

    player_info = api.get_player_info()
    village = player_info["villages"][0]
    center_x, center_y = village["x"], village["y"]

    tiles = scan_area(api, center_x, center_y, radius=5)
    save_tiles_to_json(tiles)

if __name__ == "__main__":
    main()
