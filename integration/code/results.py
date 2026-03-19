"""Race results calculation module."""
# Direct integration with leaderboard.py
from integration.code.leaderboard import Leaderboard

# Shared global leaderboard instance for integration testing
global_leaderboard = Leaderboard()

class RaceResultProcessor:
    def __init__(self, race_data):
        self.race_data = race_data  # List of raw results from race.py
        
    def calculate_points(self):
        """Calculate points from raw times and update the leaderboard."""
        valid_results = [r for r in self.race_data if r["status"] == "Completed"]
        
        if not valid_results:
            return "No teams finished the race."
            
        # Sort by fastest time
        valid_results.sort(key=lambda x: x["time"])
        
        # Award points: 1st=10, 2nd=5, 3rd=2
        point_distribution = [10, 5, 2]
        
        for idx, result in enumerate(valid_results):
            if idx < len(point_distribution):
                points = point_distribution[idx]
                global_leaderboard.update_score(result["team_id"], points)
        
        return "Results processed and leaderboard updated."
