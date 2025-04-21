# core/paths.py

import os

#This is ugly. I wish I had someone that knows how to organise python projects to talk to.
# Find the root of the project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Database paths
DATABASE_DIR = os.path.join(PROJECT_ROOT, "database")
UNOCCUPIED_OASES_DIR = os.path.join(DATABASE_DIR, "unoccupied_oases")
FULL_MAP_SCANS_DIR = os.path.join(DATABASE_DIR, "full_map_scans")
IDENTITY_FILE = os.path.join(DATABASE_DIR, "identity.json")
