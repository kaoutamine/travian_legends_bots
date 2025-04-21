import os
from typing import Optional, List
from dotenv import load_dotenv
from auth import TravianAuth, AuthCredentials
from api import TravianAPI
from models import Avatar, Coordinates, OasisInfo

class TravianClient:
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        # Load credentials from environment if not provided
        if email is None or password is None:
            load_dotenv()
            email = email or os.getenv("TRAVIAN_EMAIL")
            password = password or os.getenv("TRAVIAN_PASSWORD")
            
            if not email or not password:
                raise ValueError("Email and password must be provided either directly or through environment variables")

        self.auth = TravianAuth(AuthCredentials(email=email, password=password))
        self.api = None
        self.server_session = None
        self.current_world = None

    def login(self) -> bool:
        """Login to Travian Legends."""
        session = self.auth.login_to_lobby()
        if session:
            self.api = TravianAPI(session)
            return True
        return False

    def get_available_worlds(self) -> List[Avatar]:
        """Get list of available game worlds."""
        if not self.api:
            raise RuntimeError("Must login first")
        return self.api.get_avatars()

    def select_world(self, avatar: Avatar) -> bool:
        """Select and login to a specific game world."""
        if not self.api:
            raise RuntimeError("Must login first")
            
        try:
            self.server_session = self.api.login_to_server(avatar)
            self.current_world = avatar
            return True
        except Exception as e:
            print(f"Failed to login to world: {str(e)}")
            return False

    def get_oasis_info(self, x: int, y: int) -> Optional[OasisInfo]:
        """Get information about an oasis at specific coordinates."""
        if not self.server_session or not self.current_world:
            raise RuntimeError("Must select a world first")
            
        coords = Coordinates(x=x, y=y)
        return self.api.get_oasis_info(
            self.server_session,
            self.current_world.world.url,
            coords
        )

# Example usage
if __name__ == "__main__":
    client = TravianClient()
    
    if client.login():
        print("Successfully logged in!")
        
        # Get available worlds
        worlds = client.get_available_worlds()
        print("\nAvailable worlds:")
        for i, world in enumerate(worlds):
            print(f"[{i}] {world.world.name} — {world.world.url}")
            
        # Select first world (you might want to let user choose)
        if worlds:
            if client.select_world(worlds[0]):
                print(f"\nSuccessfully logged into {worlds[0].world.name}")
                
                # Get oasis info example
                oasis = client.get_oasis_info(x=-72, y=-22)
                if oasis:
                    print(f"\nOasis info at ({oasis.coordinates.x}, {oasis.coordinates.y}):")
                    print(f"Type: {oasis.type}")
                    print(f"Owner: {oasis.owner}")
                    if oasis.resources:
                        print("Resources:", oasis.resources) 