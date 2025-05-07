from .hero_runner import try_send_hero_to_oasis

class HeroManager:
    def __init__(self, api):
        self.api = api

    def get_hero_status(self, troops_info):
        """Check if hero is present and get health."""
        hero_count = troops_info.get("uhero", 0)
        is_present = hero_count >= 1
        
        # TODO: Implement health check if needed
        health = None
        
        return is_present, health

    def send_hero_with_escort(self, village, oasis):
        """Send hero to attack an oasis."""
        return try_send_hero_to_oasis(self.api, village, oasis) 