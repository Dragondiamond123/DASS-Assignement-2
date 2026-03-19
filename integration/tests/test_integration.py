"""Core Integration Tests for Space Mission System."""
import pytest
import random
from integration.code.registration import Team
from integration.code.race import Race
from integration.code.mission import MissionControl
from integration.code.results import RaceResultProcessor, global_leaderboard

# Fix randomness
random.seed(0)

@pytest.fixture(autouse=True)
def clear_leaderboard():
    """Automatically reset the global leaderboard before every test to prevent state leakage."""
    global_leaderboard.standings.clear()

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

    with pytest.raises(ValueError):
        race.run_race(team)

# Test 3: Results update leaderboard
def test_results_update_leaderboard():
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

    with pytest.raises(RuntimeError):
        mission.execute_mission()

# Test 6: Missing inventory condition
def test_inventory_required_for_registration():
    team = Team("Delta")
    team.roster.add_member("AA", "Pilot")
    team.roster.add_member("BB", "Engineer")

    # No Engine Core added -> should fail
    with pytest.raises(RuntimeError):
        team.complete_registration()
