from analysis.tile_analysis import analyze_tile
import logging

def is_valid_unoccupied_oasis(api, x, y):
    """
    Checks if the oasis at (x, y) is unoccupied and has no animals.
    
    :param api: TravianAPI instance
    :param x: X coordinate
    :param y: Y coordinate
    :return: True if oasis is valid for raiding (unoccupied and no animals), False otherwise
    """
    html = api.get_tile_html(x, y)
    tile_info = analyze_tile(html, (x, y))
    
    # Must be an unoccupied oasis
    if tile_info['type'] != 'unoccupied_oasis':
        logging.info(f"Skipping tile at ({x}, {y}) — Not an unoccupied oasis")
        return False
        
    # Check for animals (handle case where animals might be None)
    animals = tile_info.get('animals', {})
    if animals and any(animals.values()):
        logging.info(f"Skipping oasis at ({x}, {y}) — Animals present: {animals}")
        return False
        
    return True 