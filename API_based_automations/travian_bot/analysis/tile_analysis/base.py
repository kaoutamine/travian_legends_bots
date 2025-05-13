from dataclasses import dataclass
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from enum import Enum

class TileType(Enum):
    WILDERNESS = "wilderness"
    UNOCCUPIED_OASIS = "unoccupied_oasis"
    OCCUPIED_OASIS = "occupied_oasis"
    USER_VILLAGE = "user_village"
    NATAR_VILLAGE = "natar_village"
    EMPTY_VALLEY = "empty_valley"

@dataclass
class BaseTileAnalysis:
    """Base class for all tile analysis."""
    html: str
    coordinates: tuple
    soup: Optional[BeautifulSoup] = None
    
    def __post_init__(self):
        """Initialize BeautifulSoup parser if not provided."""
        if self.soup is None:
            self.soup = BeautifulSoup(self.html, 'html.parser')
    
    def get_title(self) -> str:
        """Get the tile's title from the HTML."""
        title_elem = self.soup.find('h1', class_='titleInHeader')
        return title_elem.text.strip() if title_elem else ""
    
    def get_tile_type(self) -> TileType:
        """Determine the type of tile based on HTML content."""
        tile_div = self.soup.find('div', id='tileDetails')
        if not tile_div:
            return TileType.WILDERNESS
        
        tile_class = tile_div.get('class', [])
        
        # Check for empty valley first
        title = self.get_title()
        if 'Abandoned valley' in title:
            founding_option = self.soup.find('span', class_='a arrow disabled', title='0/3 settlers available')
            if founding_option:
                return TileType.EMPTY_VALLEY
        
        if 'oasis' in tile_class:
            owner_info = self.soup.find('th', string='Owner')
            if owner_info and owner_info.find_next('td').text.strip():
                return TileType.OCCUPIED_OASIS
            return TileType.UNOCCUPIED_OASIS
        elif 'village' in tile_class:
            owner_info = self.soup.find('th', string='Owner')
            if owner_info and 'Natars' in owner_info.find_next('td').text:
                return TileType.NATAR_VILLAGE
            return TileType.USER_VILLAGE
        elif 'landscape' in tile_class:
            return TileType.WILDERNESS
        else:
            return TileType.WILDERNESS  # Changed from EMPTY_VALLEY to WILDERNESS as fallback
    
    def get_landscape_type(self) -> Optional[str]:
        """Get the landscape type if applicable."""
        tile_div = self.soup.find('div', id='tileDetails')
        if not tile_div:
            return None
        
        tile_class = tile_div.get('class', [])
        return next((c.split('-')[1] for c in tile_class if c.startswith('landscape-')), None)
    
    def get_village_class(self) -> Optional[str]:
        """Get the village class if applicable."""
        tile_div = self.soup.find('div', id='tileDetails')
        if not tile_div:
            return None
        
        tile_class = tile_div.get('class', [])
        return next((c for c in tile_class if c.startswith('vid')), None)
    
    def get_distance(self) -> Optional[float]:
        """Get the distance information if available."""
        distance_table = self.soup.find('table', id='distance')
        if not distance_table:
            return None
        
        distance_text = distance_table.find('td', class_='bold')
        if not distance_text:
            return None
        
        try:
            # Extract number from text like "1.4 fields"
            return float(distance_text.text.split()[0])
        except (ValueError, IndexError):
            return None 