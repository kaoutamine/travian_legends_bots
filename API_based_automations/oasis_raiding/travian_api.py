import requests

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
                            name
                        }
                        farmLists {
                            id
                            name
                            ownerVillage { id }
                        }
                    }
                }
            """
        }
        response = self.session.post(f"{self.server_url}/api/v1/graphql", json=payload)
        response.raise_for_status()
        return response.json()["data"]["ownPlayer"]

    def get_farm_list_details(self, list_id: int):
        payload = {
            "query": """
                query($id: Int!, $onlyExpanded: Boolean) {
                    farmList(id: $id) {
                        id
                        name
                        slotsAmount
                        slots(onlyExpanded: $onlyExpanded) {
                            id
                            target { x y name type }
                            troop { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 }
                        }
                    }
                }
            """,
            "variables": {
                "id": list_id,
                "onlyExpanded": False
            }
        }
        response = self.session.post(f"{self.server_url}/api/v1/graphql", json=payload)
        response.raise_for_status()
        return response.json()["data"]["farmList"]

    def get_oasis_info(self, x: int, y: int):
        payload = {
            "query": """
                query($x: Int!, $y: Int!) {
                    mapDetails(x: $x, y: $y) {
                        oasis {
                            animals {
                                type
                                count
                            }
                        }
                    }
                }
            """,
            "variables": {
                "x": x,
                "y": y
            }
        }
        response = self.session.post(f"{self.server_url}/api/v1/graphql", json=payload)
        response.raise_for_status()
        return response.json()["data"]["mapDetails"]["oasis"]
