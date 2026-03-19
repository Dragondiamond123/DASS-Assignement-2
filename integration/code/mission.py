"""Space Mission Orchestrator module."""
from integration.code.registration import Team
from integration.code.race import Race
from integration.code.results import RaceResultProcessor, global_leaderboard

class MissionControl:
    def __init__(self, mission_name):
        self.mission_name = mission_name
        self.active_teams = []
        self.races = []
        
    def add_team(self, team: Team):
        """Add a fully registered team to the mission."""
        if not team.is_registered:
            raise ValueError("Cannot add unregistered team to mission.")
        self.active_teams.append(team)
        
    def add_race(self, race: Race):
        """Add a scheduled race to the mission itinerary."""
        self.races.append(race)
        
    def execute_mission(self):
        """
        Orchestrate the entire mission flow:
        1. Run all races for all active teams.
        2. Process raw results.
        3. Return updated global standings.
        """
        if not self.active_teams or not self.races:
            raise RuntimeError("Mission needs at least 1 team and 1 race.")
            
        all_raw_results = []
        
        # Execute phase (Integration with race.py)
        for race in self.races:
            for team in self.active_teams:
                # Race returns a raw dict
                result = race.run_race(team)
                all_raw_results.append(result)
                
        # Processing phase (Integration with results.py)
        processor = RaceResultProcessor(all_raw_results)
        processor.calculate_points()
        
        # Output phase (Integration with leaderboard.py)
        return global_leaderboard.get_top_teams()
