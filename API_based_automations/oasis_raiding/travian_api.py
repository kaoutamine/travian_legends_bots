import requests
from datetime import datetime

class TravianAPI:
    def __init__(self, session: requests.Session, server_url: str):
        self.session = session
        self.server_url = server_url

    def get_villages_and_farm_lists(self):
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
        data = response.json()["data"]["ownPlayer"]
        return data

    def get_farm_lists(self, village_id: int):
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

        data = response.json()

        if isinstance(data, list):
            # If Travian sends a list, it is likely a wrapped error or weird output
            raise Exception("Unexpected list response while fetching farm lists.")

        if "data" not in data or data["data"].get("rallyPointOverview") is None:
            raise Exception("Invalid farm list response structure.")

        return data["data"]["rallyPointOverview"]["farmLists"]


    def get_oasis_info(self, x: int, y: int) -> dict:
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
        return response.json()
