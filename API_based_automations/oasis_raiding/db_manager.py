# db_manager.py

import os
import json
from datetime import datetime

# Set the database directory relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(CURRENT_DIR, 'database')

# Ensure the main database folder exists
os.makedirs(DATABASE_DIR, exist_ok=True)

def save_json(data, filename="save.json", with_timestamp=False, subfolder=None):
    """
    Save data as a JSON file inside the database directory or a subfolder.

    Args:
        data (dict or list): The data to save.
        filename (str): Desired filename (default 'save.json').
        with_timestamp (bool): Whether to add a timestamp to the filename.
        subfolder (str): Optional subfolder inside database/ to save into.
    """
    if with_timestamp:
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{ext}"

    save_dir = DATABASE_DIR
    if subfolder:
        save_dir = os.path.join(DATABASE_DIR, subfolder)
        os.makedirs(save_dir, exist_ok=True)

    path = os.path.join(save_dir, filename)

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"✅ Data saved to {path}")

def load_json(filename, subfolder=None, return_metadata=False):
    """
    Load a JSON file from the database directory or a subfolder.

    Args:
        filename (str): Filename to load.
        subfolder (str): Optional subfolder inside database/ to load from.
        return_metadata (bool): If True, return (data, metadata) tuple.

    Returns:
        dict or list: Loaded JSON content, optionally with metadata.
    """
    load_dir = DATABASE_DIR
    if subfolder:
        load_dir = os.path.join(DATABASE_DIR, subfolder)

    path = os.path.join(load_dir, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found at {path}.")

    with open(path, 'r') as f:
        content = json.load(f)

    if return_metadata and isinstance(content, dict) and "metadata" in content:
        return content.get("tiles", {}), content.get("metadata", {})
    else:
        return content
