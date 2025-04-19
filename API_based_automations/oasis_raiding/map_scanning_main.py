# map_scanning_main.py

import os
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from db_manager import save_json
from identity_handling.login import login
from identity_handling.identity_helper import load_villages_from_identity, choose_village_to_scan
from core.travian_api import TravianAPI

def parse_tile_html(html):
    """Parse the HTML content of a tile."""
    soup = BeautifulSoup(html, "html.parser")
    tile_info = {}

    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.text.strip()

        if "abandoned valley" in title.lower():
            tile_info["type"] = "oasis"
        elif "village" in title.lower() or "city" in title.lower():
            tile_info["type"] = "village"
        elif "cropland" in title.lower() or "forest" in title.lower() or "mountain" in title.lower():
            tile_info["type"] = "resource field"
        else:
            tile_info["type"] = "empty"

        tile_info["raw_title"] = title
    else:
        tile_info["type"] = "unknown"
        tile_info["raw_title"] = None

    # Bonus (e.g., +50% wood, crop, etc.)
    bonus_info = soup.find("div", class_="distribution")
    if bonus_info:
        bonuses = bonus_info.get_text(separator=" ", strip=True)
        tile_info["bonus"] = bonuses
    else:
        tile_info["bonus"] = None

    # Owner (if it's a village or occupied oasis)
    owner_tag = soup.find("div", class_="playerName")
    if owner_tag:
        tile_info["owner"] = owner_tag.text.strip()
    else:
        tile_info["owner"] = None

    return tile_info

def scan_map_area(api_client, x_start, x_end, y_start, y_end):
    """Scan the area between coordinates and parse each tile."""
    print(f"🔍 Scanning coordinates from ({x_start}, {y_start}) to ({x_end}, {y_end})...")

    scanned_data = {}
    total_tiles = (x_end - x_start + 1) * (y_end - y_start + 1)

    with tqdm(total=total_tiles, desc="🗺️  Scanning Progress", unit="tile") as pbar:
        for x in range(x_start, x_end + 1):
            for y in range(y_start, y_end + 1):
                try:
                    html = api_client.get_tile_html(x, y)
                    tile_info = parse_tile_html(html)
                    scanned_data[f"{x}_{y}"] = tile_info
                except Exception as e:
                    print(f"❌ Error scanning ({x},{y}): {e}")
                finally:
                    pbar.update(1)

    print(f"✅ Finished scanning {len(scanned_data)} tiles.")
    return scanned_data

def main():
    # Login and API setup
    session, base_url = login()
    api_client = TravianAPI(session, base_url)

    # Load villages and select scanning center
    villages = load_villages_from_identity()
    village_x, village_y = choose_village_to_scan(villages)

    # Ask for scan radius
    try:
        scan_radius = int(input("\n🗺️  Enter scan radius around the village (default = 25): ").strip())
    except ValueError:
        scan_radius = 25

    x_start = village_x - scan_radius
    x_end = village_x + scan_radius
    y_start = village_y - scan_radius
    y_end = village_y + scan_radius

    # Perform map scan
    scanned_tiles = scan_map_area(api_client, x_start, x_end, y_start, y_end)

    # Show a few scanned tiles
    print("\n📄 Sample scanned tiles:")
    for coord, info in list(scanned_tiles.items())[:5]:
        print(f"{coord}: {info}")

    # Save results
    should_save = input("\n💾 Save full map scan to database? [y/n]: ").strip().lower()
    if should_save == 'y':
        metadata = {
            "description": "Full map scan centered around village",
            "center_coordinates": f"({village_x},{village_y})",
            "scan_radius": scan_radius,
            "total_tiles": len(scanned_tiles),
        }

        save_json(
            data={"metadata": metadata, "tiles": scanned_tiles},
            filename="full_map_scan.json",
            with_timestamp=True,
            subfolder="full_map_scans"
        )
    else:
        print("❌ Scan not saved.")


if __name__ == "__main__":
    main()
