"""Mission Planning module for StreetRace Manager.
Assigns missions (delivery, rescue) and verifies required roles are available.
"""
from integration.code.registration import Team
from integration.code.race import Race
from integration.code.results import RaceResultProcessor, global_leaderboard

MISSION_TYPES = {
    "delivery": ["Driver"],
    "rescue": ["Driver", "Mechanic"],
    "recon": ["Driver", "Strategist"],
}


class MissionControl:
    """Orchestrates mission planning, race execution, and result processing."""

    def __init__(self, mission_name, mission_type="delivery"):
        self.mission_name = mission_name
        self.mission_type = mission_type
        self.active_teams = []
        self.races = []

    def add_team(self, team: Team):
        """
        Add a fully registered team to the mission.
        Business Rule 5: Missions cannot start if required roles are unavailable.
        """
        if not team.is_registered:
            raise ValueError("Cannot add unregistered team to mission.")

        # Business Rule 5: Check required roles for this mission type
        required_roles = MISSION_TYPES.get(self.mission_type, [])
        for role in required_roles:
            if not team.roster.has_role(role):
                raise RuntimeError(
                    f"Mission '{self.mission_type}' requires a {role}. "
                    f"Team '{team.name}' is missing this role."
                )

        self.active_teams.append(team)

    def add_race(self, race: Race):
        """Add a scheduled race to the mission itinerary."""
        self.races.append(race)

    def execute_mission(self):
        """
        Orchestrate the entire mission flow:
        1. Validate teams and roles.
        2. Run all races for all active teams.
        3. Process results and distribute prize money.
        4. Return updated global standings.
        """
        if not self.active_teams or not self.races:
            raise RuntimeError("Mission needs at least 1 team and 1 race.")

        all_raw_results = []

        # Execute races (Integration with race.py)
        for race in self.races:
            for team in self.active_teams:
                result = race.run_race(team)
                all_raw_results.append(result)

        # Process results (Integration with results.py → leaderboard.py → inventory.py)
        processor = RaceResultProcessor(all_raw_results)
        processor.calculate_points()

        return global_leaderboard.get_top_teams()
