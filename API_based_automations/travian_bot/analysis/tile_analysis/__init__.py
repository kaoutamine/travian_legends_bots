from typing import Dict, Any, Optional
from .base import BaseTileAnalysis, TileType
from .oasis import OasisAnalysis
from .village import VillageAnalysis
from .valley import ValleyAnalysis

def analyze_tile(html: str, coordinates: tuple) -> Dict[str, Any]:
    """
    Analyze a tile's HTML content and return structured information.
    
    Args:
        html: The HTML content of the tile
        coordinates: Tuple of (x, y) coordinates
        
    Returns:
        Dictionary containing analyzed tile information
    """
    # Create base analysis
    base_analysis = BaseTileAnalysis(html=html, coordinates=coordinates)
    tile_type = base_analysis.get_tile_type()
    
    # Initialize result with base information
    result = {
        'coordinates': coordinates,
        'type': tile_type.value,
        'title': base_analysis.get_title(),
        'landscape_type': base_analysis.get_landscape_type(),
        'distance': base_analysis.get_distance(),
    }
    
    # Add type-specific analysis
    if tile_type in [TileType.UNOCCUPIED_OASIS, TileType.OCCUPIED_OASIS]:
        oasis_analysis = OasisAnalysis(html=html, coordinates=coordinates, soup=base_analysis.soup)
        
        # Add oasis-specific information
        result.update({
            'resource_bonuses': oasis_analysis.get_resource_bonuses(),
            'attack_reports': oasis_analysis.get_attack_reports(),
        })
        
        if tile_type == TileType.UNOCCUPIED_OASIS:
            result['animals'] = oasis_analysis.get_animals()
        else:
            result['owner_info'] = oasis_analysis.get_owner_info()
            
    elif tile_type in [TileType.USER_VILLAGE, TileType.NATAR_VILLAGE]:
        village_analysis = VillageAnalysis(html=html, coordinates=coordinates, soup=base_analysis.soup)
        
        # Add village-specific information
        result.update({
            'owner_info': village_analysis.get_owner_info(),
            'population': village_analysis.get_population(),
            'buildings': village_analysis.get_buildings(),
            'attack_reports': village_analysis.get_attack_reports(),
        })
        
    elif tile_type == TileType.EMPTY_VALLEY:
        valley_analysis = ValleyAnalysis(html=html, coordinates=coordinates, soup=base_analysis.soup)
        
        # Add valley-specific information
        result.update({
            'land_distribution': valley_analysis.get_land_distribution(),
            'total_fields': valley_analysis.get_total_fields(),
            'founding_info': valley_analysis.get_founding_info(),
            'attack_reports': valley_analysis.get_attack_reports(),
        })
    
    return result

def print_tile_analysis(analysis: Dict[str, Any]) -> None:
    """
    Print a formatted version of the tile analysis.
    
    Args:
        analysis: Dictionary containing tile analysis results
    """
    print(f"\nTile Analysis for coordinates {analysis['coordinates']}:")
    print(f"Type: {analysis['type']}")
    print(f"Title: {analysis['title']}")
    
    if analysis.get('landscape_type'):
        print(f"Landscape: {analysis['landscape_type']}")
    
    if analysis.get('distance') is not None:
        print(f"Distance: {analysis['distance']} fields")
    
    # Print oasis-specific information
    if analysis['type'] in ['unoccupied_oasis', 'occupied_oasis']:
        if analysis.get('resource_bonuses'):
            print("\nResource Bonuses:")
            for resource, bonus in analysis['resource_bonuses'].items():
                if bonus > 0:
                    print(f"  {resource.capitalize()}: +{bonus}%")
        
        if analysis['type'] == 'unoccupied_oasis' and analysis.get('animals'):
            print("\nAnimals:")
            for animal, count in analysis['animals'].items():
                print(f"  {animal}: {count}")
        
        if analysis['type'] == 'occupied_oasis' and analysis.get('owner_info'):
            print("\nOwner Information:")
            for key, value in analysis['owner_info'].items():
                print(f"  {key.capitalize()}: {value}")
        
        if analysis.get('attack_reports'):
            print("\nRecent Attack Reports:")
            for report in analysis['attack_reports']:
                print(f"  - {report.get('type', 'Unknown')} by {report.get('attacker', 'Unknown')} at {report.get('time', 'Unknown')}")
    
    # Print village-specific information
    elif analysis['type'] in ['user_village', 'natar_village']:
        if analysis.get('owner_info'):
            print("\nOwner Information:")
            for key, value in analysis['owner_info'].items():
                print(f"  {key.capitalize()}: {value}")
        
        if analysis.get('population'):
            print(f"\nPopulation: {analysis['population']}")
        
        if analysis.get('land_distribution'):
            print("\nLand Distribution:")
            total = analysis.get('total_fields', 0)
            print(f"  Total Fields: {total}")
            for resource, count in analysis['land_distribution'].items():
                if count > 0:
                    print(f"  {resource.capitalize()}: {count}")
        
        if analysis.get('buildings'):
            print("\nBuildings:")
            for building, level in analysis['buildings'].items():
                print(f"  {building}: Level {level}")
    
    # Print valley-specific information
    elif analysis['type'] == 'empty_valley':
        if analysis.get('land_distribution'):
            print("\nLand Distribution:")
            total = analysis.get('total_fields', 0)
            print(f"  Total Fields: {total}")
            for resource, count in analysis['land_distribution'].items():
                if count > 0:
                    print(f"  {resource.capitalize()}: {count}")
        
        if analysis.get('founding_info'):
            print("\nFounding Information:")
            for key, value in analysis['founding_info'].items():
                print(f"  {key.capitalize()}: {value}") 