from client import TravianClient

def main():
    # Create client (will load credentials from .env file)
    client = TravianClient()
    
    # Login to Travian
    if client.login():
        print("Successfully logged in!")
        
        # Get list of available worlds
        worlds = client.get_available_worlds()
        print("\nAvailable worlds:")
        for i, world in enumerate(worlds):
            print(f"[{i}] {world.world.name} — {world.world.url}")
        
        # Let user choose a world
        selection = int(input("\nWhich world would you like to connect to? "))
        selected_world = worlds[selection]
        
        # Connect to selected world
        if client.select_world(selected_world):
            print(f"\nSuccessfully connected to {selected_world.world.name}")
            
            # Example: Get oasis info
            x = int(input("Enter oasis X coordinate: "))
            y = int(input("Enter oasis Y coordinate: "))
            
            oasis = client.get_oasis_info(x=x, y=y)
            if oasis:
                print(f"\nOasis info at ({oasis.coordinates.x}, {oasis.coordinates.y}):")
                print(f"Type: {oasis.type}")
                print(f"Owner: {oasis.owner}")
                if oasis.resources:
                    print("Resources:", oasis.resources)

if __name__ == "__main__":
    main() 