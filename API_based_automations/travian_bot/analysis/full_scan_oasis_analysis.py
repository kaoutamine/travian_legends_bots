# analysis/oasis_extractor.py

import os
import json
from datetime import datetime
from math import sqrt

from core.database_json_scan_utils import save_json_scan  # <- use the helper we built

def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def extract_unoccupied_oases(scan_path):
    """
    Loads a full map scan JSON and extracts unoccupied oases,
    saving them neatly into the corresponding coordinates folder.
    """
    with open(scan_path, "r") as f:
        scan = json.load(f)

    tiles = scan.get("tiles", {})
    metadata = scan.get("metadata", {})
    center_raw = metadata.get("center_coordinates", "(0,0)")
    center_x, center_y = map(int, center_raw.strip("()").split(","))

    village_coords_folder = f"({center_x}_{center_y})"

    print(f"[+] Loaded {len(tiles)} tiles from scan at {village_coords_folder}")

    unoccupied_oases = {}
    occupied_oases = {}

    for coords, tile_info in tiles.items():
        if tile_info.get("type") == "empty":
            title = tile_info.get("raw_title", "").lower().strip()
            if title.startswith("unoccupied oasis"):
                x_str, y_str = coords.split("_")
                x, y = int(x_str), int(y_str)
                dist = distance(center_x, center_y, x, y)
                tile_info["scanned_from"] = {
                    "center_x": center_x,
                    "center_y": center_y,
                    "distance": dist  # Store the distance directly
                }
                unoccupied_oases[coords] = tile_info
            elif "oasis" in title and not title.startswith("unoccupied oasis"):
                occupied_oases[coords] = tile_info

    print(f"[+] Unoccupied oases found: {len(unoccupied_oases)}")
    print(f"[+] Occupied oases found: {len(occupied_oases)}")

    # Sort unoccupied by distance
    sorted_unoccupied = {}
    for coords in sorted(
        unoccupied_oases.keys(),
        key=lambda c: unoccupied_oases[c]["scanned_from"]["distance"]  # Use stored distance
    ):
        sorted_unoccupied[coords] = unoccupied_oases[coords]

    # Save only unoccupied
    save_json_scan(
        data=sorted_unoccupied,
        filename="unoccupied_oases.json",
        with_timestamp=True,
        subfolder="unoccupied_oases",
        coords_folder=village_coords_folder
    )

    print(f"[+] Saved {len(sorted_unoccupied)} unoccupied oases to unoccupied_oases/{village_coords_folder}/")
    print("[+] First 5 unoccupied oases preview:")
    for idx, (coords, info) in enumerate(sorted_unoccupied.items()):
        if idx >= 5:
            break
        print(f"    {coords}: {info['raw_title']} (Distance: {info['scanned_from']['distance']:.1f} tiles)")
