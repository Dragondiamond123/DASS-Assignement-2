"""Core Integration Tests for StreetRace Manager."""
import pytest
import random
from integration.code.registration import Team
from integration.code.race import Race
from integration.code.mission import MissionControl
from integration.code.results import RaceResultProcessor, global_leaderboard

# Fix randomness for all tests to be deterministic
random.seed(0)

@pytest.fixture(autouse=True)
def clear_leaderboard():
    """Automatically reset the global leaderboard before every test."""
    global_leaderboard.standings.clear()


def make_ready_team(name="Alpha Team"):
    """Helper: Build a fully registered team with a Driver and a car."""
    team = Team(name)
    team.register_member("John Driver", "Driver", skill_level=3)
    team.register_member("Jane Mech", "Mechanic", skill_level=2)
    team.inventory.add_car("FastCar X1")
    team.complete_registration()
    return team


# Test 1: Register a driver and enter them into a race (Core scenario)
def test_register_and_race():
    """Registering a driver and then entering a race must succeed."""
    team = make_ready_team("Alpha Team")
    
    race = Race("Track1", 2)
    result = race.run_race(team)
    
    assert result["status"] == "Completed"


# Test 2: Race without registration must fail (Business Rule)
def test_race_without_registration():
    """Attempting to race without a registered team must raise ValueError."""
    team = Team("Beta")
    team.register_member("JJ Doe", "Driver")
    team.inventory.add_car("Car Y")
    # Not calling complete_registration() on purpose
    
    race = Race("Track1", 2)
    with pytest.raises(ValueError):
        race.run_race(team)


# Test 3: Results update leaderboard AND cash balance (Business Rule 4)
def test_results_update_leaderboard_and_inventory():
    """Race results must update both the global leaderboard and team cash balance."""
    team1 = make_ready_team("Team T1")
    team2 = make_ready_team("Team T2")

    data = [
        {"team_id": team1.team_id, "status": "Completed", "time": 50,
         "prize": 2000, "team": team1},
        {"team_id": team2.team_id, "status": "Completed", "time": 60,
         "prize": 2000, "team": team2},
    ]

    processor = RaceResultProcessor(data)
    processor.calculate_points()

    # Leaderboard check
    assert global_leaderboard.standings[team1.team_id] == 10
    # Inventory cash balance must have increased (Business Rule 4)
    assert team1.inventory.cash_balance > 5000


# Test 4: Mission execution end-to-end
def test_mission_execution():
    """A complete mission run must return a leaderboard result."""
    team = make_ready_team("Gamma Team")
    
    mission = MissionControl("Mission1", mission_type="delivery")
    mission.add_team(team)
    mission.add_race(Race("Track1", 2))
    
    result = mission.execute_mission()
    
    assert isinstance(result, list)


# Test 5: Mission without team must raise RuntimeError
def test_mission_no_team():
    """Starting a mission with no teams must raise RuntimeError."""
    mission = MissionControl("M1")
    
    with pytest.raises(RuntimeError):
        mission.execute_mission()


# Test 6: Missing inventory (no car) blocks registration (Business Rule)
def test_inventory_required_for_registration():
    """A team without a car in inventory cannot complete registration."""
    team = Team("Delta Team")
    team.register_member("Mike Driver", "Driver")
    # No car added -> should fail

    with pytest.raises(RuntimeError):
        team.complete_registration()


# Test 7: Mission requiring Mechanic fails if no Mechanic on team
def test_mission_missing_required_role():
    """A rescue mission requires both Driver and Mechanic roles (Business Rule 5)."""
    team = Team("Echo Team")
    team.register_member("Sam Driver", "Driver")
    team.inventory.add_car("Rescue Van")
    team.complete_registration()
    
    mission = MissionControl("Rescue Op", mission_type="rescue")
    
    with pytest.raises(RuntimeError, match="requires a Mechanic"):
        mission.add_team(team)


# Test 8: Complete race end-to-end and verify prize money updates inventory
def test_race_prize_updates_inventory():
    """Completing a race and verifying results and prize money update the inventory."""
    team = make_ready_team("Prize Team")
    initial_cash = team.inventory.cash_balance  # 5000

    race = Race("Grand Prix", 3)   # prize = 3000
    result = race.run_race(team)

    # Process race result through the results module
    processor = RaceResultProcessor([result])
    processor.calculate_points()

    # Business Rule 4: Cash balance must have increased by prize money
    assert team.inventory.cash_balance > initial_cash


# Test 9: Damaged car mission requires mechanic check
def test_damaged_car_requires_mechanic():
    """If a car is damaged, a rescue mission requiring a mechanic must verify availability."""
    team = Team("Repair Crew")
    team.register_member("Ace Racer", "Driver")
    # No mechanic added — can't do a rescue/repair mission
    team.inventory.add_car("Damaged Car")
    team.complete_registration()

    mission = MissionControl("Emergency Repair", mission_type="rescue")

    # Business Rule 3: Requires Mechanic, but team has none
    with pytest.raises(RuntimeError, match="requires a Mechanic"):
        mission.add_team(team)


# Test 10: A crew member must be registered before entering a race
def test_crew_must_register_before_race():
    """Business Rule 1: A crew member must be registered before a role can be assigned and used."""
    team = Team("Unregistered Crew")
    # Add a Driver but do not register the team
    team.register_member("Quick Sam", "Driver")
    team.inventory.add_car("Speedy Car")
    # Intentionally skipping complete_registration()

    race = Race("Sprint", 1)
    with pytest.raises(ValueError, match="not officially registered"):
        race.run_race(team)

