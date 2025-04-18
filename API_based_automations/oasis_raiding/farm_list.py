# oasis_raiding/farm_list.py

import requests
from datetime import datetime

def fetch_villages(session: requests.Session) -> list:
    url = "https://ts3.x1.asia.travian.com/api/v1/graphql"
    payload = {
        "query": """
            query {
                ownPlayer {
                    villages { id name sortIndex tribeId hasHarbour }
                    currentVillageId
                }
            }
        """
    }
    response = session.post(url, json=payload)
    response.raise_for_status()
    data = response.json()["data"]["ownPlayer"]["villages"]

    villages = []
    for v in data:
        villages.append({
            "id": v["id"],
            "name": v["name"],
            "tribe_id": v["tribeId"],
            "has_harbour": v["hasHarbour"],
        })
    return villages

def fetch_farm_lists(session: requests.Session, village_id: int) -> list:
    url = "https://ts3.x1.asia.travian.com/api/v1/graphql"
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
    response = session.post(url, json=payload)
    response.raise_for_status()
    data = response.json()["data"]["rallyPointOverview"]["farmLists"]

    farm_lists = []
    for fl in data:
        farm_lists.append({
            "id": fl["id"],
            "name": fl["name"],
            "slots_amount": fl["slotsAmount"],
            "running_raids": fl["runningRaidsAmount"],
            "last_started_time": fl["lastStartedTime"],
        })
    return farm_lists

def fetch_farm_list_details(session: requests.Session, farm_list_id: int) -> dict:
    url = "https://ts3.x1.asia.travian.com/api/v1/graphql"
    payload = {
        "query": """
            query($id: Int!, $onlyExpanded: Boolean) {
                farmList(id: $id) {
                    id
                    name
                    slots(onlyExpanded: $onlyExpanded) {
                        id
                        target {
                            id
                            x
                            y
                            name
                            type
                            population
                        }
                        distance
                        isActive
                        isRunning
                        lastRaid {
                            time
                            booty { resourceType { id code } amount }
                            bootyMax
                        }
                        totalBooty { booty raids }
                    }
                }
            }
        """,
        "variables": {"id": farm_list_id, "onlyExpanded": False}
    }
    response = session.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def parse_farm_list(farm_list_data: dict) -> list:
    slots = farm_list_data["data"]["farmList"]["slots"]
    parsed_slots = []

    for slot in slots:
        target = slot["target"]
        loot = {}
        last_raid = slot.get("lastRaid")

        if last_raid and last_raid.get("booty"):
            for res in last_raid["booty"]:
                loot[res["resourceType"]["code"]] = res["amount"]

        parsed_slots.append({
            "target_name": target["name"],
            "x": target["x"],
            "y": target["y"],
            "population": target["population"],
            "type": "Oasis" if target["type"] == 2 else "Village",
            "distance": slot["distance"],
            "loot": loot,
            "total_loot": sum(loot.values()),
            "is_running": slot["isRunning"],
        })
    
    return parsed_slots
