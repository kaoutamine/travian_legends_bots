# map_scanning_main.py

from db_manager import save_json
from identity_handling.login import login
from travian_api import TravianAPI
from bs4 import BeautifulSoup

def scan_map_area(api_client, x_start, x_end, y_start, y_end):
    print(f"🔍 Scanning coordinates from ({x_start}, {y_start}) to ({x_end}, {y_end})...")
    scanned_data = {}

    for x in range(x_start, x_end + 1):
        for y in range(y_start, y_end + 1):
            html = api_client.get_tile_html(x, y)
            tile_info = parse_tile_html(html)
            scanned_data[f"{x}_{y}"] = tile_info

    print(f"✅ Scanned {len(scanned_data)} tiles.")
    return scanned_data

def parse_tile_html(html):
    soup = BeautifulSoup(html, "html.parser")
    tile_info = {}

    title = soup.find("h1")
    if title:
        tile_info["title"] = title.text.strip()

    # You can extend this parsing: resource bonuses, owner, type, etc.

    return tile_info

def main():
    # Login
    session, base_url = login()
    api_client = TravianAPI(session, base_url)

    # Define area to scan
    x_start, x_end = 100, 102
    y_start, y_end = 100, 102

    scanned_tiles = scan_map_area(api_client, x_start, x_end, y_start, y_end)

    # Show sample
    print("\nSample tiles scanned:")
    for coord, info in list(scanned_tiles.items())[:5]:
        print(f"{coord}: {info}")

    # Ask to save
    should_save = input("\n💾 Save scan results to database? [y/n]: ").strip().lower()
    if should_save == 'y':
        metadata = {
            "description": "Small map scan",
            "area_scanned": f"({x_start},{y_start}) to ({x_end},{y_end})",
            "tiles_scanned": len(scanned_tiles),
        }
        save_json({"metadata": metadata, "tiles": scanned_tiles}, filename="map_scan.json", with_timestamp=True)
    else:
        print("❌ Scan not saved.")

if __name__ == "__main__":
    main()
