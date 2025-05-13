from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from .base import BaseTileAnalysis, TileType

@dataclass
class VillageAnalysis(BaseTileAnalysis):
    """Specialized analysis for village tiles (both user and Natar villages)."""
    
    def get_land_distribution(self) -> Dict[str, int]:
        """Get the distribution of resource fields in the village."""
        fields = {'wood': 0, 'clay': 0, 'iron': 0, 'crop': 0}
        
        # Find the land distribution table - try both possible IDs
        dist_table = self.soup.find('table', id='distribution')
        if not dist_table:
            dist_table = self.soup.find('table', id='land_distribution')
        if not dist_table:
            return fields
            
        # Parse each resource field
        for row in dist_table.find_all('tr'):
            icon = row.find('i')
            val = row.find('td', class_='val')
            desc = row.find('td', class_='desc')
            
            if icon and val and desc:
                resource_class = icon.get('class', [''])[0]
                try:
                    # Handle both numeric values and percentages
                    count_text = val.text.strip().replace('\u202d', '').replace('\u202c', '').rstrip('%')
                    count = int(count_text)
                    
                    if 'r1' in resource_class:
                        fields['wood'] = count
                    elif 'r2' in resource_class:
                        fields['clay'] = count
                    elif 'r3' in resource_class:
                        fields['iron'] = count
                    elif 'r4' in resource_class:
                        fields['crop'] = count
                except ValueError:
                    continue
                    
        return fields
    
    def get_total_fields(self) -> int:
        """Get the total number of resource fields in the village."""
        fields = self.get_land_distribution()
        return sum(fields.values())
    
    def get_owner_info(self) -> Optional[Dict[str, str]]:
        """Get information about the village owner."""
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
    
    def get_population(self) -> Optional[int]:
        """Get the village population."""
        pop_table = self.soup.find('table', id='population')
        if not pop_table:
            return None
            
        pop_cell = pop_table.find('td', class_='val')
        if not pop_cell:
            return None
            
        try:
            return int(pop_cell.text.strip())
        except ValueError:
            return None
    
    def get_resource_production(self) -> Dict[str, int]:
        """Get the village's resource production rates."""
        production = {'wood': 0, 'clay': 0, 'iron': 0, 'crop': 0}
        
        prod_table = self.soup.find('table', id='production')
        if not prod_table:
            return production
            
        for row in prod_table.find_all('tr'):
            resource_cell = row.find('td', class_='res')
            rate_cell = row.find('td', class_='rate')
            
            if resource_cell and rate_cell:
                resource = resource_cell.text.strip().lower()
                try:
                    rate = int(rate_cell.text.strip())
                    production[resource] = rate
                except ValueError:
                    continue
                    
        return production
    
    def get_buildings(self) -> Dict[str, int]:
        """Get information about buildings in the village."""
        buildings = {}
        buildings_table = self.soup.find('table', id='buildings')
        if not buildings_table:
            return buildings
            
        for row in buildings_table.find_all('tr'):
            name_cell = row.find('td', class_='name')
            level_cell = row.find('td', class_='level')
            
            if name_cell and level_cell:
                name = name_cell.text.strip()
                try:
                    level = int(level_cell.text.strip())
                    buildings[name] = level
                except ValueError:
                    continue
                    
        return buildings
    
    def get_attack_reports(self) -> List[Dict[str, str]]:
        """Get recent attack reports for the village."""
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