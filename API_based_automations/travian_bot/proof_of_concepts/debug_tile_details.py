"""
Proof of Concept: Debug Tile Details
This file is kept for reference and future development.
It demonstrates the basic tile analysis functionality.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity_handling.login import login
from core.travian_api import TravianAPI
from analysis.tile_analysis import analyze_tile, print_tile_analysis

def main():
    # Load environment variables
    load_dotenv()
    
    # Login to the server and initialize API
    print("Logging into the server...")
    session, server_url = login()
    api = TravianAPI(session, server_url)
    
    # Test tiles with their coordinates and expected types
    test_tiles = [
        (27, -39),  # Wilderness
        (35, -30),  # Occupied oasis
        (38, -28),  # User village
        (36, -39),  # Natar village
        (36, -36),  # Empty valley
        (39, -38),  # Wilderness
    ]
    
    print("\n🔍 Testing Tile Analysis System")
    print("=" * 50)
    
    for x, y in test_tiles:
        try:
            print(f"\n📌 Testing tile at ({x}, {y})...")
            
            # Get tile HTML
            html = api.get_tile_html(x, y)
            if not html:
                print(f"❌ Failed to get HTML for tile at ({x}, {y})")
                continue
            
            # Print raw HTML for debugging
            print("\n--- RAW HTML START ---")
            print(html[:2000] + ("..." if len(html) > 2000 else ""))  # Print up to 2000 chars
            print("--- RAW HTML END ---\n")
            
            # Analyze tile
            analysis = analyze_tile(html, (x, y))
            
            # Print analysis results
            print_tile_analysis(analysis)
            
        except Exception as e:
            print(f"❌ Error processing tile at ({x}, {y}): {str(e)}")
    
    print("\n✅ Tile analysis test complete!")

if __name__ == "__main__":
    main() 