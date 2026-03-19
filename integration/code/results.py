"""Results module for StreetRace Manager.
Records race outcomes, updates rankings, and handles prize money.
"""
from integration.code.leaderboard import Leaderboard

# Shared global leaderboard instance
global_leaderboard = Leaderboard()

# Prize money distribution factors
PRIZE_DISTRIBUTION = [1.0, 0.6, 0.3]  # 1st gets 100%, 2nd 60%, 3rd 30%


class RaceResultProcessor:
    """Processes race results and distributes prize money to teams."""

    def __init__(self, race_data):
        self.race_data = race_data  # List of raw results from race.py

    def calculate_points(self):
        """
        Rank teams by time, award points, and credit prize money 
        directly into each team's inventory cash balance.
        Business Rule 4: Race results update the cash balance in the Inventory.
        """
        valid_results = [r for r in self.race_data if r["status"] == "Completed"]

        if not valid_results:
            return "No teams finished the race."

        # Sort by fastest time
        valid_results.sort(key=lambda x: x["time"])

        # Award points and prize money
        point_distribution = [10, 5, 2]

        for idx, result in enumerate(valid_results):
            if idx < len(point_distribution):
                points = point_distribution[idx]
                global_leaderboard.update_score(result["team_id"], points)

            # Business Rule 4: Credit prize money to team's inventory
            if idx < len(PRIZE_DISTRIBUTION) and "team" in result:
                prize = int(result["prize"] * PRIZE_DISTRIBUTION[idx])
                result["team"].inventory.add_prize_money(prize)

        return "Results processed and leaderboard updated."
