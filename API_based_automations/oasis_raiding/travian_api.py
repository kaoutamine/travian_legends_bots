# Update for travian_api.py

import requests

class TravianAPI:
    def __init__(self, session: requests.Session, server_url: str):
        self.session = session
        self.server_url = server_url.rstrip('/')

    def get_villages_and_farm_lists(self):
        url = f"{self.server_url}/api/v1/graphql"
        payload = {"query": "query{ownPlayer{currentVillageId villages{id sortIndex name tribeId hasHarbour} farmLists{name ownerVillage{id}}}}"}
        r = self.session.post(url, json=payload)
        r.raise_for_status()
        data = r.json()["data"]["ownPlayer"]
        villages = data["villages"]
        farm_lists = data["farmLists"]
        return villages, farm_lists

    def get_farm_list_details(self, farm_list_id: int):
        url = f"{self.server_url}/api/v1/graphql"
        payload = {
            "query": """
            query($id: Int!, $onlyExpanded: Boolean){
                farmList(id: $id) {
                    slots(onlyExpanded: $onlyExpanded) {
                        id
                        target { id mapId x y name type population }
                        distance
                        isActive
                        isRunning
                        lastRaid { booty { resourceType { code } amount } }
                    }
                }
            }
            """,
            "variables": {"id": farm_list_id, "onlyExpanded": False}
        }
        r = self.session.post(url, json=payload)
        r.raise_for_status()
        return r.json()["data"]["farmList"]["slots"]

    def get_map_info(self, x: int, y: int):
        url = f"{self.server_url}/api/v1/map/position"
        payload = {
            "data": {
                "x": x,
                "y": y,
                "zoomLevel": 1,
                "ignorePositions": []
            }
        }
        r = self.session.post(url, json=payload)
        r.raise_for_status()
        return r.json()

    def check_oasis_for_monsters(self, x: int, y: int):
        map_info = self.get_map_info(x, y)
        oases = []
        for pos in map_info.get("oasis", []):
            oasis = {
                "x": pos["x"],
                "y": pos["y"],
                "hasMonsters": pos.get("animals", []) != []
            }
            oases.append(oasis)
        return oases

    def list_farm_oases_with_monsters(self, farm_list_id: int):
        slots = self.get_farm_list_details(farm_list_id)
        oasis_info = []

        for slot in slots:
            target = slot["target"]
            if target["type"] == 2:  # Type 2 is Oasis
                monsters = self.check_oasis_for_monsters(target["x"], target["y"])
                for mon in monsters:
                    oasis_info.append({
                        "target_name": target["name"],
                        "x": target["x"],
                        "y": target["y"],
                        "has_monsters": mon["hasMonsters"]
                    })
        return oasis_info
