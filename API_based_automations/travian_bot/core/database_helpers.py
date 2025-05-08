# core/database_helpers.py

import os
import json
import glob
from datetime import datetime
from core.paths import UNOCCUPIED_OASES_DIR  # We'll set this properly in paths.py

def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def load_latest_unoccupied_oases(village_coords):
    """Load the latest unoccupied oases file for a given village coordinates.
    
    Args:
        village_coords (str): Village coordinates in format "(x_y)"
    """
    base_path = os.path.join("database", "unoccupied_oases", village_coords)
    if not os.path.exists(base_path):
        print(f"[📂] No unoccupied oases directory found for {village_coords}")
        return {}

    print(f"[📂] Looking for unoccupied oases in: {os.path.abspath(base_path)}")
    files = glob.glob(os.path.join(base_path, "unoccupied_oases_*.json"))
    if not files:
        print(f"[📂] No unoccupied oases files found in {base_path}")
        return {}

    latest_file = max(files, key=os.path.getctime)
    print(f"[+] Using latest unoccupied oases file: {os.path.basename(latest_file)}")

    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            oases = json.load(f)
            
            # Extract village coordinates from the folder name
            village_x, village_y = map(int, village_coords.strip("()").split("_"))
            
            # Add distance to each oasis
            for coords, oasis in oases.items():
                oasis_x, oasis_y = map(int, coords.split("_"))
                oasis["distance"] = calculate_distance(village_x, village_y, oasis_x, oasis_y)
                
            return oases
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"[❌] Error loading unoccupied oases: {e}")
        return {}
