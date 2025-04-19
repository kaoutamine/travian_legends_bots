import requests
import re
from bs4 import BeautifulSoup

class TravianAPI:
    def __init__(self, session: requests.Session, server_url: str):
        self.session = session
        self.server_url = server_url

    def get_player_info(self):
        payload = {
            "query": """
                query {
                    ownPlayer {
                        currentVillageId
                        villages {
                            id
                            sortIndex
                            name
                            tribeId
                            hasHarbour
                        }
                        farmLists {
                            id
                            name
                            ownerVillage {
                                id
                            }
                        }
                    }
                }
            """
        }
        response = self.session.post(f"{self.server_url}/api/v1/graphql", json=payload)
        response.raise_for_status()
        return response.json()["data"]["ownPlayer"]

    def get_village_farm_lists(self, village_id: int) -> list:
        payload = {
            "query": """
                query($villageId: Int!) {
                    rallyPointOverview(villageId: $villageId) {
                        farmLists {
                            id
                            name
                            slotsAmount
                            runningRaidsAmount
                            lastStartedTime
                        }
                    }
                }
            """,
            "variables": {"villageId": village_id}
        }
        response = self.session.post(f"{self.server_url}/api/v1/graphql", json=payload)
        response.raise_for_status()
        return response.json()["data"]["rallyPointOverview"]["farmLists"]

    def get_farm_list_details(self, farm_list_id: int) -> dict:
        payload = {
            "query": """
                query($id: Int!, $onlyExpanded: Boolean) {
                    farmList(id: $id) {
                        id
                        name
                        slotsAmount
                        runningRaidsAmount
                        slots(onlyExpanded: $onlyExpanded) {
                            id
                            target {
                                id
                                mapId
                                x
                                y
                                name
                                type
                                population
                            }
                            troop {
                                t1 t2 t3 t4 t5 t6 t7 t8 t9 t10
                            }
                        }
                    }
                }
            """,
            "variables": {
                "id": farm_list_id,
                "onlyExpanded": False
            }
        }
        response = self.session.post(f"{self.server_url}/api/v1/graphql", json=payload)
        response.raise_for_status()
        return response.json()["data"]["farmList"]

    def get_oasis_animal_count(self, x: int, y: int) -> int:
        """Fetch animal count using tile-details API."""
        url = f"{self.server_url}/api/v1/map/tile-details"
        payload = {"x": x, "y": y}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        html = data.get("html")
        if not html:
            return 0

        soup = BeautifulSoup(html, "html.parser")
        troop_table = soup.find("table", id="troop_info")
        if not troop_table:
            return 0

        animal_count = 0
        for row in troop_table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 2:
                count_text = cols[1].get_text(strip=True).replace("\u202d", "").replace("\u202c", "")
                try:
                    count = int(count_text)
                    animal_count += count
                except ValueError:
                    continue
        return animal_count

    def prepare_oasis_attack(self, map_id: int, x: int, y: int, troops: dict) -> dict:
        """Prepare attack (fetch action and checksum) after triggering troop setup."""
        # First POST to trigger checksum generation
        url = f"{self.server_url}/build.php?gid=16&tt=2"

        payload = {
            "x": x,
            "y": y,
            "eventType": 4,
            "ok": "ok",
            "villagename": "",
        }
        for troop_id in range(1, 11):
            payload[f"troop[t{troop_id}]"] = troops.get(f"t{troop_id}", "")

        res = self.session.post(url, data=payload)
        res.raise_for_status()

        html = res.text

        # Now extract action and checksum
        action_match = re.search(r'name="action" value="([^"]+)"', html)
        checksum_match = re.search(r'name="checksum" value="([^"]+)"', html)

        if not action_match or not checksum_match:
            raise Exception("Failed to find action/checksum when preparing attack (after troop setup POST).")

        return {
            "action": action_match.group(1),
            "checksum": checksum_match.group(1)
        }


    def confirm_oasis_attack(self, attack_info: dict, x: int, y: int, troops: dict, village_id: int) -> bool:
        """Confirm and launch the attack."""
        payload = {
            "action": attack_info["action"],
            "eventType": 4,
            "villagename": "",
            "x": x,
            "y": y,
            "redeployHero": "",
            "checksum": attack_info["checksum"],
        }

        for troop_id in range(1, 11):
            payload[f"troops[0][t{troop_id}]"] = troops.get(f"t{troop_id}", 0)

        payload["troops[0][villageId]"] = village_id

        response = self.session.post(f"{self.server_url}/build.php?gid=16&tt=2", data=payload)
        response.raise_for_status()

        if "Raid sent" in response.text or "The troops are on their way" in response.text:
            return True
        return False
