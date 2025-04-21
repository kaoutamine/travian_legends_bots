import os
import json

# === NEW LOCATION CONSTANTS ===
DATABASE_FOLDER = os.path.join(os.path.dirname(__file__), "..", "database")
ENTITY_FILE = os.path.join(DATABASE_FOLDER, "entities.json")

# Make sure database folder exists
os.makedirs(DATABASE_FOLDER, exist_ok=True)

def load_entities():
    if not os.path.exists(ENTITY_FILE):
        return {}
    with open(ENTITY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_entities(entities):
    with open(ENTITY_FILE, "w", encoding="utf-8") as f:
        json.dump(entities, f, indent=2)

# Everything else you had in entity_handler stays the same
