"""Global leaderboard management."""

class Leaderboard:
    def __init__(self):
        self.standings = {}  # team_id -> points

    def update_score(self, team_id, points):
        """Update a team's global score."""
        self.standings[team_id] = self.standings.get(team_id, 0) + points

    def get_top_teams(self, limit=5):
        """Return the top teams sorted by points descending."""
        # Sort dictionary by values (points) descending
        sorted_standings = sorted(self.standings.items(), key=lambda x: x[1], reverse=True)
        return sorted_standings[:limit]
