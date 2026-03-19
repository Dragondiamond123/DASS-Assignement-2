"""Core Integration Tests for Space Mission System."""
import pytest
from integration.code.registration import Team
from integration.code.race import Race
from integration.code.mission import MissionControl
from integration.code.results import RaceResultProcessor, global_leaderboard

# Test 1: Register + race success
def test_register_and_race():
    team = Team("Alpha")
    team.roster.add_member("AA", "Pilot")
    team.roster.add_member("BB", "Engineer")
    team.inventory.add_part("Engine Core", 1)

    team.complete_registration()

    race = Race("Track1", 2)
    result = race.run_race(team)

    assert result["status"] == "Completed"

# Test 2: Race without registration
def test_race_without_registration():
    team = Team("Beta")
    race = Race("Track1", 2)

    try:
        race.run_race(team)
        assert False
    except ValueError:
        assert True

# Test 3: Results update leaderboard
def test_results_update_leaderboard():
    global_leaderboard.standings.clear()

    data = [
        {"team_id": "T1", "status": "Completed", "time": 50},
        {"team_id": "T2", "status": "Completed", "time": 60},
    ]

    processor = RaceResultProcessor(data)
    processor.calculate_points()

    assert global_leaderboard.standings["T1"] == 10

# Test 4: Mission execution
def test_mission_execution():
    team = Team("Gamma")
    team.roster.add_member("AA", "Pilot")
    team.roster.add_member("BB", "Engineer")
    team.inventory.add_part("Engine Core", 1)
    team.complete_registration()

    mission = MissionControl("Mission1")
    mission.add_team(team)
    mission.add_race(Race("Track1", 2))

    result = mission.execute_mission()

    assert isinstance(result, list)

# Test 5: Mission without team
def test_mission_no_team():
    mission = MissionControl("M1")

    try:
        mission.execute_mission()
        assert False
    except RuntimeError:
        assert True
