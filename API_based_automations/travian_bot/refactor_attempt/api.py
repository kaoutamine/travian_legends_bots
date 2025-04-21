import requests
from typing import List, Optional
from models import Avatar, GameWorld, Coordinates, OasisInfo

class TravianAPI:
    def __init__(self, session: requests.Session):
        self.session = session

    def get_avatars(self) -> List[Avatar]:
        """Get list of available avatars (game worlds) for the user."""
        graphql_url = "https://lobby.legends.travian.com/api/graphql"
        graphql_payload = {
            "variables": {},
            "query": """
            {
              avatars {
                uuid
                name
                gameworld {
                  metadata {
                    url
                    name
                  }
                }
              }
            }
            """
        }
        
        response = self.session.post(graphql_url, json=graphql_payload)
        response.raise_for_status()
        data = response.json()["data"]["avatars"]

        return [
            Avatar(
                uuid=a["uuid"],
                name=a["name"],
                world=GameWorld(
                    name=a["gameworld"]["metadata"]["name"],
                    url=a["gameworld"]["metadata"]["url"]
                )
            )
            for a in data
        ]

    def login_to_server(self, avatar: Avatar) -> requests.Session:
        """Login to a specific game world."""
        try:
            # Get redirect code
            play_url = f"https://lobby.legends.travian.com/api/avatar/play/{avatar.uuid}"
            print(f"Attempting to play avatar at URL: {play_url}")
            
            # Print current session cookies for debugging
            print("Current session cookies:", self.session.cookies.get_dict())
            
            play_resp = self.session.post(play_url)
            print(f"Play response status: {play_resp.status_code}")
            print(f"Play response headers: {play_resp.headers}")
            
            if play_resp.status_code != 200:
                print(f"Error response body: {play_resp.text}")
                play_resp.raise_for_status()
                
            play_data = play_resp.json()
            print(f"Play response data: {play_data}")
            
            if "code" not in play_data:
                raise ValueError(f"No code found in response: {play_data}")
                
            code = play_data["code"]

            # Follow redirect to get authenticated in the game world
            server_session = requests.Session()
            server_session.cookies.update(self.session.cookies.get_dict())
            
            server_auth_url = f"{avatar.world.url.rstrip('/')}/api/v1/auth?code={code}&response_type=redirect"
            print(f"Attempting server auth at URL: {server_auth_url}")
            
            auth_resp = server_session.get(server_auth_url, allow_redirects=True)
            print(f"Auth response status: {auth_resp.status_code}")
            print(f"Auth response headers: {auth_resp.headers}")
            
            if auth_resp.status_code != 200:
                print(f"Error response body: {auth_resp.text}")
                auth_resp.raise_for_status()

            return server_session
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Error response: {e.response.text}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    def get_oasis_info(self, server_session: requests.Session, world_url: str, coords: Coordinates) -> Optional[OasisInfo]:
        """Get information about an oasis at specific coordinates."""
        oasis_url = f"{world_url}/ajax.php"
        params = {"cmd": "mapDetails", "x": coords.x, "y": coords.y}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
            "Referer": f"{world_url}/karte.php?x={coords.x}&y={coords.y}"
        }

        response = server_session.get(oasis_url, headers=headers, params=params)
        response.raise_for_status()
        
        # Parse response and return OasisInfo object
        # Note: You'll need to implement the actual parsing logic based on the response format
        data = response.json()
        return OasisInfo(
            coordinates=coords,
            type=data.get("type", ""),
            owner=data.get("owner"),
            troops=data.get("troops"),
            resources=data.get("resources")
        ) 