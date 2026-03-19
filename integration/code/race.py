"""Race simulation module."""
import random

class Race:
    def __init__(self, track_name, difficulty):
        self.track_name = track_name
        self.difficulty = difficulty  # 1 (Easy) to 5 (Hard)

    def run_race(self, team):
        """
        Simulate a race for a verified Team. 
        Returns a raw race_time dict object based on team's attributes.
        """
        if not team.is_registered:
            raise ValueError("Team is not officially registered for racing!")
            
        # Consume fuel for the race (Requires Integration with inventory.py)
        if not team.inventory.consume_fuel(self.difficulty * 100):
            return {"team_id": team.team_id, "status": "DNF", "reason": "Out of Fuel"}

        # Calculate performance based on crew size
        crew_efficiency = len(team.roster.members) * 10
        
        # Base time minus efficiency, plus random obstacle factor
        # Higher difficulty increases base time
        base_time = self.difficulty * 100
        completion_time = base_time - crew_efficiency + random.randint(0, 50)
        
        return {
            "team_id": team.team_id,
            "status": "Completed", 
            "time": completion_time
        }
