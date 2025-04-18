# farm_list.py

import requests
from datetime import datetime

def fetch_villages_and_farm_lists(session: requests.Session) -> dict:
    """
    Fetch the player's villages and basic farm list info (name, owner village ID).
    Does NOT return farm list IDs.
    """
    url = "https://ts3.x1.asia.travian.com/api/v1/graphql"
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
    response = session.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return {
        "villages": data["data"]["ownPlayer"]["villages"],
        "farmLists": data["data"]["ownPlayer"]["farmLists"]
    }

def fetch_farm_lists_with_ids(session: requests.Session, village_id: int) -> list:
    """
    Fetch farm lists for a specific village, including their IDs and slots amount.
    """
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
        "variables": {
            "villageId": village_id
        }
    }
    response = session.post(url, json=payload)
    response.raise_for_status()
    data = response.json()

    farm_lists = []
    for fl in data["data"]["rallyPointOverview"]["farmLists"]:
        farm_lists.append({
            "id": fl["id"],
            "name": fl["name"],
            "slots_amount": fl["slotsAmount"],
            "running_raids": fl["runningRaidsAmount"],
            "last_started_time": fl["lastStartedTime"],
        })
    return farm_lists

def fetch_farm_list(session: requests.Session, list_id: int) -> dict:
    """
    Fetch detailed information about a specific farm list by its ID.
    Includes all slots and their last raid results.
    """
    url = "https://ts3.x1.asia.travian.com/api/v1/graphql"
    payload = {
        "query": """
            query($id: Int!, $onlyExpanded: Boolean){
                bootstrapData { timestamp }
                weekendWarrior { isNightTruce }
                farmList(id: $id) {
                    id
                    name
                    slotsAmount
                    runningRaidsAmount
                    isExpanded
                    sortIndex
                    lastStartedTime
                    sortField
                    sortDirection
                    useShip
                    onlyLosses
                    ownerVillage {
                        id
                        troops {
                            ownTroopsAtTown {
                                units { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 }
                            }
                        }
                    }
                    defaultTroop { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 }
                    slotStates: slots { id isActive }
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
                        troop { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 }
                        distance
                        isActive
                        isRunning
                        isSpying
                        runningAttacks
                        nextAttackAt
                        lastRaid {
                            reportId
                            authKey
                            time
                            booty {
                                resourceType { id code }
                                amount
                            }
                            bootyMax
                            icon
                        }
                        totalBooty { booty raids }
                    }
                }
            }
        """,
        "variables": {
            "id": list_id,
            "onlyExpanded": False
        }
    }
    response = session.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def parse_farm_list(farm_list_data: dict) -> list:
    """
    Parse farm list data into a cleaner structure for easier processing.
    """
    slots = farm_list_data['data']['farmList']['slots']
    parsed_slots = []

    for slot in slots:
        target = slot['target']
        last_raid = slot.get('lastRaid')
        
        loot = {}
        if last_raid and last_raid['booty']:
            for res in last_raid['booty']:
                loot[res['resourceType']['code']] = res['amount']

        parsed_slots.append({
            "target_name": target['name'],
            "x": target['x'],
            "y": target['y'],
            "population": target['population'],
            "type": "Oasis" if target['type'] == 2 else "Village",
            "distance": slot['distance'],
            "loot": loot,
            "total_loot": sum(loot.values()),
            "is_running": slot['isRunning'],
            "next_attack_at": datetime.utcfromtimestamp(slot['nextAttackAt']) if slot['nextAttackAt'] else None,
        })

    return parsed_slots
