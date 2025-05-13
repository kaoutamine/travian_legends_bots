from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from .base import BaseTileAnalysis, TileType

@dataclass
class OasisAnalysis(BaseTileAnalysis):
    """Specialized analysis for oasis tiles."""
    
    def get_owner_info(self) -> Optional[Dict[str, str]]:
        """Get information about the oasis owner if occupied."""
        if self.get_tile_type() != TileType.OCCUPIED_OASIS:
            return None
            
        owner_info = {}
        owner_table = self.soup.find('table', id='village_info')
        if not owner_table:
            return None
            
        # Get tribe
        tribe_row = owner_table.find('tr', class_='first')
        if tribe_row:
            tribe_cell = tribe_row.find('td')
            if tribe_cell:
                owner_info['tribe'] = tribe_cell.text.strip()
            
        # Get alliance
        alliance_row = owner_table.find('tr')
        if alliance_row:
            alliance_cell = alliance_row.find('td')
            if alliance_cell:
                alliance_link = alliance_cell.find('a')
                if alliance_link:
                    owner_info['alliance'] = alliance_link.text.strip()
                else:
                    owner_info['alliance'] = alliance_cell.text.strip()
            
        return owner_info if owner_info else None
    
    def get_resource_bonuses(self) -> Dict[str, int]:
        """Get resource bonuses for the oasis."""
        bonuses = {'wood': 0, 'clay': 0, 'iron': 0, 'crop': 0}
        
        # Find the resource bonus table
        bonus_table = self.soup.find('table', id='distribution')
        if not bonus_table:
            return bonuses
            
        # Parse each resource bonus
        for row in bonus_table.find_all('tr'):
            icon = row.find('i')
            val = row.find('td', class_='val')
            desc = row.find('td', class_='desc')
            
            if icon and val and desc:
                resource_class = icon.get('class', [''])[0]
                try:
                    bonus = int(val.text.strip().replace('\u202d', '').replace('\u202c', '').rstrip('%'))
                    resource_type = desc.text.strip().lower()
                    
                    if 'r1' in resource_class:
                        bonuses['wood'] = bonus
                    elif 'r2' in resource_class:
                        bonuses['clay'] = bonus
                    elif 'r3' in resource_class:
                        bonuses['iron'] = bonus
                    elif 'r4' in resource_class:
                        bonuses['crop'] = bonus
                except ValueError:
                    continue
                    
        return bonuses
    
    def get_animals(self) -> Optional[Dict[str, int]]:
        """Get information about animals in unoccupied oases."""
        if self.get_tile_type() != TileType.UNOCCUPIED_OASIS:
            return None
            
        animals = {}
        troop_table = self.soup.find('table', id='troop_info')
        if not troop_table:
            return None
            
        # Parse animal information
        for row in troop_table.find_all('tr'):
            img = row.find('img')
            cols = row.find_all('td')
            if img and len(cols) >= 2:
                animal_name = img.get('alt', '').strip().lower()
                count_text = cols[1].get_text(strip=True).replace('\u202d', '').replace('\u202c', '')
                try:
                    count = int(count_text)
                    animals[animal_name] = count
                except ValueError:
                    continue
                    
        return animals if animals else None
    
    def get_attack_reports(self) -> List[Dict[str, str]]:
        """Get recent attack reports for the oasis."""
        reports = []
        reports_table = self.soup.find('table', id='reports')
        if not reports_table:
            return reports
            
        for row in reports_table.find_all('tr'):
            report = {}
            
            # Get report type
            type_cell = row.find('td', class_='type')
            if type_cell:
                report['type'] = type_cell.text.strip()
                
            # Get attacker info
            attacker_cell = row.find('td', class_='attacker')
            if attacker_cell:
                report['attacker'] = attacker_cell.text.strip()
                
            # Get timestamp
            time_cell = row.find('td', class_='time')
            if time_cell:
                report['time'] = time_cell.text.strip()
                
            if report:
                reports.append(report)
                
        return reports 