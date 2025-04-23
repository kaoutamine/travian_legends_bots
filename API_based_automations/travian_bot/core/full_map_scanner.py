# core/full_map_scanner.py

from tqdm import tqdm
from bs4 import BeautifulSoup
from core.database_json_scan_utils import save_json_scan

def parse_tile_html(html):
    soup = BeautifulSoup(html, "html.parser")
    tile_info = {}

    title_tag = soup.find("h1")
    if title_tag:
        title = title_tag.text.strip()
        if "abandoned valley" in title.lower():
            tile_info["type"] = "oasis"
        elif "village" in title.lower() or "city" in title.lower():
            tile_info["type"] = "village"
        elif any(word in title.lower() for word in ["cropland", "forest", "mountain"]):
            tile_info["type"] = "resource field"
        else:
            tile_info["type"] = "empty"
        tile_info["raw_title"] = title
    else:
        tile_info["type"] = "unknown"
        tile_info["raw_title"] = None

    bonus_info = soup.find("div", class_="distribution")
    tile_info["bonus"] = bonus_info.get_text(separator=" ", strip=True) if bonus_info else None

    owner_tag = soup.find("div", class_="playerName")
    tile_info["owner"] = owner_tag.text.strip() if owner_tag else None

    return tile_info

def scan_map_area(api_client, x_start, x_end, y_start, y_end):
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

    return scanned_data

def full_map_scan(api_client, village_x, village_y, scan_radius=25):
    x_start = village_x - scan_radius
    x_end = village_x + scan_radius
    y_start = village_y - scan_radius
    y_end = village_y + scan_radius

    scanned_tiles = scan_map_area(api_client, x_start, x_end, y_start, y_end)

    metadata = {
        "description": "Full map scan centered around village",
        "center_coordinates": f"({village_x},{village_y})",
        "scan_radius": scan_radius,
        "total_tiles": len(scanned_tiles),
    }

    village_coords_folder = f"({village_x}_{village_y})"

    scan_save_path = save_json_scan(
        data={"metadata": metadata, "tiles": scanned_tiles},
        filename="full_map_scan.json",
        with_timestamp=True,
        subfolder="full_map_scans",
        coords_folder=village_coords_folder,
        return_path=True
    )

    return scan_save_path
