import os
from .hero_runner import try_send_hero_to_oasis
import logging
import json
import re
import html
from dataclasses import dataclass
from typing import Optional, Tuple
from bs4 import BeautifulSoup

@dataclass
class HeroStatus:
    is_present: bool
    health: Optional[float]
    is_on_mission: bool
    mission_return_time: Optional[str]
    mission_target: Optional[Tuple[int, int]]
    current_village_id: Optional[str]
    current_village_name: Optional[str]
    is_in_known_village: bool
    level: Optional[int]
    experience: Optional[int]
    experience_percent: Optional[float]

class HeroManager:
    def __init__(self, api):
        self.api = api

    def _is_known_village(self, village_id: str) -> bool:
        """Check if village_id exists in identity.json."""
        try:
            current_dir = os.path.dirname(__file__)
            database_dir = os.path.join(current_dir, '..', 'database')
            identity_path = os.path.join(database_dir, 'identity.json')
            identity_path = os.path.abspath(identity_path)

            with open(identity_path, "r", encoding="utf-8") as f:
                identity = json.load(f)
            for server in identity.get("travian_identity", {}).get("servers", []):
                for village in server.get("villages", []):
                    if str(village.get("village_id")) == str(village_id):
                        return True
            return False
        except Exception as e:
            logging.error(f"Failed to check village in identity: {e}")
            return False

    def _extract_village_info(self, status_title: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract village ID and name from hero status title."""
        try:
            # Look for village ID in URL
            did_match = re.search(r'newdid=(\d+)', status_title)
            village_id = did_match.group(1) if did_match else None
            
            # Look for village name in HTML
            name_match = re.search(r'>([^<]+)</a>', status_title)
            village_name = name_match.group(1) if name_match else None
            
            return village_id, village_name
        except Exception as e:
            logging.error(f"Failed to extract village info: {e}")
            return None, None

    def fetch_hero_status(self) -> Optional[HeroStatus]:
        """Fetch hero status from the HUD API endpoint."""
        try:
            response = self.api.session.get(f"{self.api.server_url}/api/v1/hero/dataForHUD")
            response.raise_for_status()
            data = response.json()
            
            # Debug: Print raw response
            logging.debug("Raw hero HUD response:")
            logging.debug(json.dumps(data, indent=2))
            
            # Extract village_id from 'url' field
            url = data.get("url", "")
            village_id = None
            url_match = re.search(r"newdid=(\d+)", url)
            if url_match:
                village_id = url_match.group(1)
            
            # Extract village_name from heroStatusTitle <a> tag (unescape first)
            village_name = None
            status_title = data.get("heroStatusTitle", "")
            status_title_unescaped = html.unescape(status_title)
            name_match = re.search(r">([^<]+)</a>", status_title_unescaped)
            if name_match:
                village_name = name_match.group(1)
            
            is_in_known_village = self._is_known_village(village_id) if village_id else False
            
            # Determine if hero is on mission
            is_on_mission = "heroHome" not in data.get("statusInlineIcon", "")
            
            return HeroStatus(
                is_present=data.get("healthStatus") == "alive",
                health=data.get("health"),
                is_on_mission=is_on_mission,
                mission_return_time=None,  # TODO: Extract from mission info if available
                mission_target=None,  # TODO: Extract from mission info if available
                current_village_id=village_id,
                current_village_name=village_name,
                is_in_known_village=is_in_known_village,
                level=data.get("level"),
                experience=data.get("experience"),
                experience_percent=data.get("experiencePercent")
            )
            
        except Exception as e:
            logging.error(f"Failed to fetch hero status: {e}")
            return None

    def send_hero_with_escort(self, village, oasis):
        """Send hero to attack an oasis."""
        return try_send_hero_to_oasis(self.api, village, oasis) 