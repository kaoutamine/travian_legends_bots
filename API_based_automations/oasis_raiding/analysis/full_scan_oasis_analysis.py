import os
import json
from datetime import datetime
from glob import glob
from math import sqrt

def distance(x1, y1, x2, y2):
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)

def extract_unoccupied_oases():
    scans_dir = "API_based_automations/oasis_raiding/database/full_map_scans/"
    output_dir = "API_based_automations/oasis_raiding/database/unoccupied_oases/"

    os.makedirs(output_dir, exist_ok=True)

    # Find the most recent full scan
    scan_files = glob(os.path.join(scans_dir, "*.json"))
    if not scan_files:
        print("[-] No full map scan found in", scans_dir)
        return

    latest_scan_file = max(scan_files, key=os.path.getmtime)
    print(f"[+] Using latest map scan: {os.path.basename(latest_scan_file)}")

    # Load scan
    with open(latest_scan_file, "r") as f:
        scan = json.load(f)

    tiles = scan.get("tiles", {})
    metadata = scan.get("metadata", {})
    center_raw = metadata.get("center_coordinates", "(0,0)")
    center_x, center_y = map(int, center_raw.strip("()").split(","))

    # Try to grab assigned village name if it exists (optional upgrade later)
    assigned_village = metadata.get("assigned_village", "Unknown")

    print(f"[+] Loaded {len(tiles)} tiles from the map scan.")
    print(f"[+] Center coordinates: ({center_x}, {center_y})")
    print(f"[+] Assigned to village: {assigned_village}")

    # Analyze tiles
    unoccupied_oases = {}
    occupied_oases = {}

    for coords, tile_info in tiles.items():
        if tile_info.get("type") == "empty":
            title = tile_info.get("raw_title", "").lower().strip()
            if title.startswith("unoccupied oasis"):
                # Add village assignment
                tile_info["scanned_from"] = {
                    "village_name": assigned_village,
                    "center_x": center_x,
                    "center_y": center_y,
                }
                unoccupied_oases[coords] = tile_info
            elif "oasis" in title and not title.startswith("unoccupied oasis"):
                occupied_oases[coords] = tile_info

    print(f"[+] Unoccupied oases found: {len(unoccupied_oases)}")
    print(f"[+] Occupied oases found: {len(occupied_oases)}")

    # Sort by distance
    sorted_unoccupied = {}
    for coords in sorted(unoccupied_oases.keys(), key=lambda c: distance(center_x, center_y, int(c.split("_")[0]), int(c.split("_")[1]))):
        sorted_unoccupied[coords] = unoccupied_oases[coords]

    # Save only the unoccupied ones
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"unoccupied_oases_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(sorted_unoccupied, f, indent=4)

    print(f"[+] Saved extracted and sorted unoccupied oases into: {output_file}")
    print("[+] First 5 unoccupied oases preview:")

    for idx, (coords, info) in enumerate(sorted_unoccupied.items()):
        if idx >= 5:
            break
        print(f"    {coords}: {info['raw_title']} (from {info['scanned_from']['village_name']})")

if __name__ == "__main__":
    extract_unoccupied_oases()
