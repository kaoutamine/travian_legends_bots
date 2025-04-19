import time
import json
from bs4 import BeautifulSoup
import re

class Tile:
    def __init__(self, x, y, map_id, tile_type, bonus=None, troop_info=None, player_info=None):
        self.x = x
        self.y = y
        self.map_id = map_id
        self.tile_type = tile_type
        self.bonus = bonus
        self.troop_info = troop_info
        self.player_info = player_info

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "mapId": self.map_id,
            "tileType": self.tile_type,
            "bonus": self.bonus,
            "troopInfo": self.troop_info,
            "playerInfo": self.player_info
        }




def parse_html_to_tile(html, x, y):
    

    soup = BeautifulSoup(html, "html.parser")

    # Try to detect oasis
    if "oasis" in soup.find("div", id="tileDetails")["class"]:
        tile_type = "oasis"
        bonus_table = soup.find("table", id="distribution")
        bonus = None
        if bonus_table:
            bonus = {}
            for tr in bonus_table.find_all("tr"):
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    resource = cells[2].text.strip()
                    percentage = cells[1].text.strip()
                    bonus[resource] = percentage

        # Troop info (animals)
        troop_table = soup.find("table", id="troop_info")
        troop_info = []
        if troop_table:
            for row in troop_table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 3:
                    unit_name = cols[2].text.strip()
                    try:
                        unit_count = int(cols[1].text.strip())
                    except:
                        unit_count = 0
                    troop_info.append({"unit": unit_name, "count": unit_count})
        
        return Tile(x, y, None, tile_type, bonus, troop_info, None)

    # Else probably village
    title = soup.find("h1", class_="titleInHeader")
    if title and "village" in title.text.lower():
        tile_type = "village"
        # TODO: parse player name, village name, population if available
        return Tile(x, y, None, tile_type)

    # Else fallback to field
    return Tile(x, y, None, "field")
