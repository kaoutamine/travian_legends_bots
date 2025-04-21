# core/database_helpers.py

import os
import json
from glob import glob
from core.paths import UNOCCUPIED_OASES_DIR  # We'll set this properly in paths.py

def load_latest_unoccupied_oases(village_folder):
    """
    Load the latest unoccupied oases JSON for a specific village.
    
    Args:
        village_folder (str): Folder name in the format (x_y) corresponding to the village.
    
    Returns:
        dict: Loaded oases data, or None if not found.
    """
    folder_path = os.path.join(UNOCCUPIED_OASES_DIR, village_folder)
    folder_path = os.path.abspath(folder_path)

    print(f"[📂] Looking for unoccupied oases in: {folder_path}")

    if not os.path.isdir(folder_path):
        print(f"[-] Folder does not exist: {folder_path}")
        return None

    scan_files = glob(os.path.join(folder_path, "*.json"))
    if not scan_files:
        print(f"[-] No JSON files found in {folder_path}")
        return None

    latest_file = max(scan_files, key=os.path.getmtime)
    print(f"[+] Using latest unoccupied oases file: {os.path.basename(latest_file)}")

    with open(latest_file, "r") as f:
        oases = json.load(f)

    return oases
