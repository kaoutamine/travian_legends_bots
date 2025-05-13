from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
from bs4 import BeautifulSoup
import re

class TileType(Enum):
    WILDERNESS = "wilderness"
    UNOCCUPIED_OASIS = "unoccupied_oasis"
    OCCUPIED_OASIS = "occupied_oasis"
    USER_VILLAGE = "user_village"
    NATAR_VILLAGE = "natar_village"
    EMPTY_VALLEY = "empty_valley"

@dataclass
class ResourceDistribution:
    wood: int = 0
    clay: int = 0
    iron: int = 0
    crop: int = 0
    wood_bonus: int = 0  # Percentage bonus
    clay_bonus: int = 0  # Percentage bonus
    iron_bonus: int = 0  # Percentage bonus
    crop_bonus: int = 0  # Percentage bonus
    resource_types: Dict[str, str] = None  # Maps resource to type (e.g., "wood" -> "Woodcutters")

    def __post_init__(self):
        if self.resource_types is None:
            self.resource_types = {}

    def has_bonus(self) -> bool:
        return any([self.wood_bonus, self.clay_bonus, self.iron_bonus, self.crop_bonus])

    def has_production(self) -> bool:
        return any([self.wood, self.clay, self.iron, self.crop])

@dataclass
class TroopInfo:
    wild_boar: int = 0
    wolf: int = 0
    bear: int = 0

@dataclass
class TileInfo:
    type: TileType
    title: str
    coordinates: tuple
    village_class: Optional[str] = None
    resources: Optional[ResourceDistribution] = None
    troops: Optional[TroopInfo] = None
    landscape_type: Optional[str] = None

def analyze_tile(html_content: str, coordinates: tuple) -> TileInfo:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get title and determine tile type
    title_elem = soup.find('h1', class_='titleInHeader')
    title = title_elem.text.strip() if title_elem else ""
    
    # Initialize landscape_type to None
    landscape_type = None
    
    # Determine tile type based on class and content
    tile_div = soup.find('div', id='tileDetails')
    if not tile_div:
        return TileInfo(type=TileType.WILDERNESS, title="Unknown", coordinates=coordinates)
    
    tile_class = tile_div.get('class', [])
    tile_type = None
    
    if 'oasis' in tile_class:
        # Check if occupied by looking for owner info
        owner_info = soup.find('th', string='Owner')
        if owner_info and owner_info.find_next('td').text.strip():
            tile_type = TileType.OCCUPIED_OASIS
        else:
            tile_type = TileType.UNOCCUPIED_OASIS
    elif 'village' in tile_class:
        # Check if NATAR village
        owner_info = soup.find('th', string='Owner')
        if owner_info and 'Natars' in owner_info.find_next('td').text:
            tile_type = TileType.NATAR_VILLAGE
        else:
            tile_type = TileType.USER_VILLAGE
    elif 'landscape' in tile_class:
        tile_type = TileType.WILDERNESS
        # Get landscape type
        landscape_type = next((c.split('-')[1] for c in tile_class if c.startswith('landscape-')), None)
    else:
        tile_type = TileType.EMPTY_VALLEY

    # Get village class if applicable
    village_class = None
    if tile_type in [TileType.USER_VILLAGE, TileType.NATAR_VILLAGE, TileType.EMPTY_VALLEY]:
        village_class = next((c for c in tile_class if c.startswith('vid')), None)
        if village_class:
            village_class = village_class.replace('vid', 'village')

    # Parse resources
    resources = ResourceDistribution()
    resource_table = soup.find('table', id='distribution')
    if resource_table:
        # Check if it's a bonus table (has td.val with %)
        bonus_rows = resource_table.find_all('td', class_='val')
        if bonus_rows and any('%' in row.text for row in bonus_rows):
            # Parse bonus percentages
            for row in resource_table.find_all('tr'):
                icon = row.find('i')
                if not icon:
                    continue
                val = row.find('td', class_='val')
                if not val:
                    continue
                resource_class = icon.get('class', [''])[0]
                # Extract only digits (handle unicode and RTL chars)
                bonus_str = re.sub(r'[^0-9]', '', val.text)
                if not bonus_str:
                    continue
                bonus = int(bonus_str)
                if 'r1' in resource_class:
                    resources.wood_bonus = bonus
                elif 'r2' in resource_class:
                    resources.clay_bonus = bonus
                elif 'r3' in resource_class:
                    resources.iron_bonus = bonus
                elif 'r4' in resource_class:
                    resources.crop_bonus = bonus
        else:
            # Parse resource production
            for row in resource_table.find_all('tr'):
                icon = row.find('i')
                if not icon:
                    continue
                val = row.find('td', class_='val')
                if not val:
                    continue
                resource_class = icon.get('class', [''])[0]
                amount = int(val.text.strip())
                resource_type = row.find('td', class_='desc')
                if resource_type:
                    resource_type = resource_type.text.strip()
                if 'r1' in resource_class:
                    resources.wood = amount
                    if resource_type:
                        resources.resource_types['wood'] = resource_type
                elif 'r2' in resource_class:
                    resources.clay = amount
                    if resource_type:
                        resources.resource_types['clay'] = resource_type
                elif 'r3' in resource_class:
                    resources.iron = amount
                    if resource_type:
                        resources.resource_types['iron'] = resource_type
                elif 'r4' in resource_class:
                    resources.crop = amount
                    if resource_type:
                        resources.resource_types['crop'] = resource_type

    # Parse troops for unoccupied oases
    troops = None
    if tile_type == TileType.UNOCCUPIED_OASIS:
        troops = TroopInfo()
        troop_table = soup.find('table', id='troop_info')
        if troop_table:
            for row in troop_table.find_all('tr'):
                text = row.text.strip()
                if 'Wild Boar' in text:
                    troops.wild_boar = int(text.split(':')[1].strip())
                elif 'Wolf' in text:
                    troops.wolf = int(text.split(':')[1].strip())
                elif 'Bear' in text:
                    troops.bear = int(text.split(':')[1].strip())

    return TileInfo(
        type=tile_type,
        title=title,
        coordinates=coordinates,
        village_class=village_class,
        resources=resources,
        troops=troops,
        landscape_type=landscape_type
    )

def print_tile_analysis(tile_info: TileInfo):
    print("\n" + "="*50)
    print(f"Tile Analysis for {tile_info.coordinates}")
    print("="*50)
    print(f"Type: {tile_info.type.value}")
    print(f"Title: {tile_info.title}")
    
    if tile_info.village_class:
        print(f"Village Class: {tile_info.village_class}")
    
    if tile_info.landscape_type:
        print(f"Landscape Type: {tile_info.landscape_type}")
    
    if tile_info.resources:
        if tile_info.resources.has_bonus():
            print("\nResource Bonuses:")
            if tile_info.resources.wood_bonus:
                print(f"- Wood: +{tile_info.resources.wood_bonus}%")
            if tile_info.resources.clay_bonus:
                print(f"- Clay: +{tile_info.resources.clay_bonus}%")
            if tile_info.resources.iron_bonus:
                print(f"- Iron: +{tile_info.resources.iron_bonus}%")
            if tile_info.resources.crop_bonus:
                print(f"- Crop: +{tile_info.resources.crop_bonus}%")
        
        if tile_info.resources.has_production():
            print("\nResource Production:")
            if tile_info.resources.wood:
                type_str = f" ({tile_info.resources.resource_types.get('wood', '')})" if 'wood' in tile_info.resources.resource_types else ""
                print(f"- Wood: {tile_info.resources.wood}{type_str}")
            if tile_info.resources.clay:
                type_str = f" ({tile_info.resources.resource_types.get('clay', '')})" if 'clay' in tile_info.resources.resource_types else ""
                print(f"- Clay: {tile_info.resources.clay}{type_str}")
            if tile_info.resources.iron:
                type_str = f" ({tile_info.resources.resource_types.get('iron', '')})" if 'iron' in tile_info.resources.resource_types else ""
                print(f"- Iron: {tile_info.resources.iron}{type_str}")
            if tile_info.resources.crop:
                type_str = f" ({tile_info.resources.resource_types.get('crop', '')})" if 'crop' in tile_info.resources.resource_types else ""
                print(f"- Crop: {tile_info.resources.crop}{type_str}")
    
    if tile_info.troops:
        print("\nTroops:")
        if tile_info.troops.wild_boar:
            print(f"- Wild Boar: {tile_info.troops.wild_boar}")
        if tile_info.troops.wolf:
            print(f"- Wolf: {tile_info.troops.wolf}")
        if tile_info.troops.bear:
            print(f"- Bear: {tile_info.troops.bear}") 