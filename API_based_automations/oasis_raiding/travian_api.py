# Travian API Modular Farm List Management

import requests

class TravianAPI:
    def __init__(self, session: requests.Session, server_url: str):
        self.session = session
        self.server_url = server_url.rstrip("/")

    def _graphql_query(self, query: str, variables: dict = None) -> dict:
        url = f"{self.server_url}/api/v1/graphql"
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def fetch_villages_and_farm_lists(self) -> dict:
        query = """
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
        data = self._graphql_query(query)
        return data["data"]["ownPlayer"]

    def fetch_farm_list_details(self, farm_list_id: int) -> dict:
        query = """
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
                                units {
                                    t1 t2 t3 t4 t5 t6 t7 t8 t9 t10
                                }
                            }
                        }
                    }
                    defaultTroop {
                        t1 t2 t3 t4 t5 t6 t7 t8 t9 t10
                    }
                    slotStates: slots {
                        id
                        isActive
                    }
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
                        totalBooty {
                            booty
                            raids
                        }
                    }
                }
            }
        """
        variables = {"id": farm_list_id, "onlyExpanded": False}
        data = self._graphql_query(query, variables)
        return data["data"]["farmList"]

    def parse_farm_list_slots(self, farm_list_data: dict) -> list:
        parsed_slots = []
        slots = farm_list_data.get("slots", [])
        for slot in slots:
            target = slot.get("target", {})
            loot = {}
            last_raid = slot.get("lastRaid")
            if last_raid and last_raid.get("booty"):
                for res in last_raid["booty"]:
                    loot[res["resourceType"]["code"]] = res["amount"]

            parsed_slots.append({
                "target_name": target.get("name", "Unknown"),
                "x": target.get("x"),
                "y": target.get("y"),
                "population": target.get("population"),
                "type": "Oasis" if target.get("type") == 2 else "Village",
                "distance": slot.get("distance"),
                "loot": loot,
                "total_loot": sum(loot.values()),
                "is_running": slot.get("isRunning"),
                "next_attack_at": slot.get("nextAttackAt"),
            })
        return parsed_slots
