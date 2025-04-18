# farm_list.py

import requests
from datetime import datetime

def fetch_farm_list(session: requests.Session, list_id: int) -> dict:
    url = "https://ts3.x1.asia.travian.com/api/v1/graphql"
    payload = {
        "query": """
            query($id: Int!, $onlyExpanded: Boolean){
                bootstrapData { timestamp }
                weekendWarrior { isNightTruce }
                farmList(id: $id) {
                    id name slotsAmount runningRaidsAmount isExpanded sortIndex lastStartedTime sortField sortDirection useShip onlyLosses
                    ownerVillage {
                        id
                        troops { ownTroopsAtTown { units { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 } } }
                    }
                    defaultTroop { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 }
                    slotStates: slots { id isActive }
                    slots(onlyExpanded: $onlyExpanded) {
                        id
                        target { id mapId x y name type population }
                        troop { t1 t2 t3 t4 t5 t6 t7 t8 t9 t10 }
                        distance
                        isActive
                        isRunning
                        isSpying
                        runningAttacks
                        nextAttackAt
                        lastRaid {
                            reportId authKey time
                            booty { resourceType { id code } amount }
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
