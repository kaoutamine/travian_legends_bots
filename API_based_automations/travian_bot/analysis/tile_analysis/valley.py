from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from bs4 import BeautifulSoup
from .base import BaseTileAnalysis, TileType

@dataclass
class ValleyAnalysis(BaseTileAnalysis):
    """Specialized analysis for valley tiles."""
    
    def get_resource_production(self) -> Dict[str, int]:
        """Get the valley's resource production rates."""
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
    
    def get_founding_info(self) -> Optional[Dict[str, str]]:
        """Get information about founding a new village in this valley."""
        if self.get_tile_type() != TileType.EMPTY_VALLEY:
            return None
            
        founding_info = {}
        founding_table = self.soup.find('table', id='founding')
        if not founding_table:
            return None
            
        # Get founding requirements
        reqs_cell = founding_table.find('td', class_='requirements')
        if reqs_cell:
            founding_info['requirements'] = reqs_cell.text.strip()
            
        # Get founding cost
        cost_cell = founding_table.find('td', class_='cost')
        if cost_cell:
            founding_info['cost'] = cost_cell.text.strip()
            
        return founding_info if founding_info else None
    
    def get_attack_reports(self) -> List[Dict[str, str]]:
        """Get recent attack reports for the valley."""
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
    
    def get_land_distribution(self) -> Dict[str, int]:
        """Get the distribution of resource fields in the valley."""
        fields = {'wood': 0, 'clay': 0, 'iron': 0, 'crop': 0}
        
        # Find the land distribution table
        dist_table = self.soup.find('table', id='distribution')
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
                    count = int(val.text.strip())
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
        """Get the total number of resource fields in the valley."""
        fields = self.get_land_distribution()
        return sum(fields.values()) 