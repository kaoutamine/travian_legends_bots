import os
import json
from datetime import datetime

# Set the database directory relative to this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(CURRENT_DIR, 'database')

# Ensure the database folder exists
os.makedirs(DATABASE_DIR, exist_ok=True)


def save_json(data, filename=None, with_timestamp=False):
    """
    Save data as a JSON file inside the database directory.

    Args:
        data (dict or list): The data to save.
        filename (str): Desired filename (without path). Default 'save.json'.
        with_timestamp (bool): Whether to add a timestamp to the filename.
    """
    if filename is None:
        filename = "save.json"
    if with_timestamp:
        base, ext = os.path.splitext(filename)
        filename = f"{base}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{ext}"
    path = os.path.join(DATABASE_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"✅ Data saved to {path}")


def load_json(filename):
    """
    Load a JSON file from the database directory.

    Args:
        filename (str): Filename to load (without path).

    Returns:
        dict or list: Loaded JSON content.
    """
    path = os.path.join(DATABASE_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {filename} not found in database folder.")
    with open(path, 'r') as f:
        return json.load(f)
