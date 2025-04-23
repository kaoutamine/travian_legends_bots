import os
import json
from datetime import datetime

def save_json_scan(data, filename, with_timestamp=False, subfolder=None, coords_folder=None, return_path=False):
    # Find the true project root dynamically (wherever the script is)
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Build base_dir relative to that
    base_dir = os.path.join(root_dir, "../database/")  # database folder is one level above core/

    if subfolder:
        base_dir = os.path.join(base_dir, subfolder)

    if coords_folder:
        coords_folder = coords_folder.replace(" ", "_")
        base_dir = os.path.join(base_dir, coords_folder)

    os.makedirs(base_dir, exist_ok=True)

    if with_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename.split('.')[0]}_{timestamp}.json"

    full_path = os.path.join(base_dir, filename)

    with open(full_path, "w") as f:
        json.dump(data, f, indent=4)

    if return_path:
        return os.path.abspath(full_path)
