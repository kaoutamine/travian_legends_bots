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

    def prepare_oasis_attack(self, map_id: int, x: int, y: int, troop_setup: dict) -> dict:
        """Prepare an attack on a given oasis and return action and checksum."""
        # 1. Open raid preparation page (GET)
        url = f"{self.server_url}/build.php?gid=16&tt=2&eventType=4&targetMapId={map_id}"
        res = self.session.get(url)
        res.raise_for_status()

        # 2. Send troop setup (POST)
        prepare_data = {
            "villagename": "",
            "x": x,
            "y": y,
            "eventType": 4,
            "ok": "ok",
        }
        for troop_id in range(1, 12):  # t1 to t11
            prepare_data[f"troop[t{troop_id}]"] = troop_setup.get(f"t{troop_id}", 0)
        prepare_data["troop[scoutTarget]"] = ""
        prepare_data["troop[catapultTarget1]"] = ""
        prepare_data["troop[catapultTarget2]"] = ""

        troop_preparation_res = self.session.post(f"{self.server_url}/build.php?gid=16&tt=2", data=prepare_data)
        troop_preparation_res.raise_for_status()

        # 3. Parse action and checksum
        soup = BeautifulSoup(troop_preparation_res.text, "html.parser")

        # Find action
        action_input = soup.select_one('input[name="action"]')
        if not action_input:
            raise Exception("[-] No action input found during preparation.")
        action = action_input["value"]

        # Find checksum from Confirm button
        button = soup.find("button", id="confirmSendTroops")
        if not button:
            raise Exception("[-] Confirm button not found during preparation.")
        onclick = button.get("onclick")
        checksum_match = re.search(r"value\s*=\s*'([a-f0-9]+)'", onclick)
        if not checksum_match:
            raise Exception("[-] Checksum not found in onclick during preparation.")
        checksum = checksum_match.group(1)

        return {
            "action": action,
            "checksum": checksum,
        }



    def confirm_oasis_attack(self, attack_info: dict, x: int, y: int, troops: dict, village_id: int) -> bool:
        """Confirm and send the final attack based on prepared action and checksum."""
        final_payload = {
            "action": attack_info["action"],
            "eventType": 4,
            "villagename": "",
            "x": x,
            "y": y,
            "redeployHero": "",
            "checksum": attack_info["checksum"],
        }

        for troop_id in range(1, 12):
            final_payload[f"troops[0][t{troop_id}]"] = troops.get(f"t{troop_id}", 0)

        final_payload["troops[0][scoutTarget]"] = ""
        final_payload["troops[0][catapultTarget1]"] = ""
        final_payload["troops[0][catapultTarget2]"] = ""
        final_payload["troops[0][villageId]"] = village_id

        res = self.session.post(f"{self.server_url}/build.php?gid=16&tt=2", data=final_payload, allow_redirects=False)
        res.raise_for_status()

        # Detect success based on 302 redirect
        return res.status_code == 302 and res.headers.get("Location") == "/build.php?gid=16&tt=1"
    

    def get_tile_html(self, x, y):
        url = f"{self.server_url}/api/v1/map/tile-details"
        res = self.session.post(url, json={"x": x, "y": y})
        res.raise_for_status()
        return res.json()["html"]


