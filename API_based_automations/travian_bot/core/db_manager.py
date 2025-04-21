import os
import json
from datetime import datetime

# Set the database directory relative to the project root
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")

# Ensure the main database folder exists
os.makedirs(DATABASE_DIR, exist_ok=True)

def save_json(data, filename="save.json", with_timestamp=False, subfolder=None):
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
