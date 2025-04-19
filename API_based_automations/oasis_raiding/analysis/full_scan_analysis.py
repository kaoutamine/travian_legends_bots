import os
import json
from datetime import datetime
from glob import glob

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

    print(f"[+] Loaded {len(tiles)} tiles from the map scan.")

    # Analyze tiles
    unoccupied_oases = {}
    occupied_oases = {}

    for coords, tile_info in tiles.items():
        if tile_info.get("type") == "empty":
            title = tile_info.get("raw_title", "").lower().strip()
            if title.startswith("unoccupied oasis"):
                unoccupied_oases[coords] = tile_info
            elif "oasis" in title and not title.startswith("unoccupied oasis"):
                occupied_oases[coords] = tile_info

    print(f"[+] Unoccupied oases found: {len(unoccupied_oases)}")
    print(f"[+] Occupied oases found: {len(occupied_oases)}")

    # Save only the unoccupied ones
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"unoccupied_oases_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(unoccupied_oases, f, indent=4)

    print(f"[+] Saved extracted unoccupied oases into: {output_file}")
    print("[+] First 5 unoccupied oases preview:")

    for idx, (coords, info) in enumerate(unoccupied_oases.items()):
        if idx >= 5:
            break
        print(f"    {coords}: {info['raw_title']}")

if __name__ == "__main__":
    extract_unoccupied_oases()
