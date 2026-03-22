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
    """Helper: Build a fully registered team with a Driver and a ready car."""
    team = Team(name)
    # Business Rule 1: Register first, then assign role
    team.register_member("John Driver")
    team.assign_team_role("John Driver", "Driver", skill_level=3)
    
    team.register_member("Jane Mech")
    team.assign_team_role("Jane Mech", "Mechanic", skill_level=2)
    
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


# Test 2: Race without registration must fail
def test_race_without_registration():
    """Attempting to race without a registered team must raise ValueError."""
    team = Team("Beta")
    team.register_member("JJ Doe")
    team.assign_team_role("JJ Doe", "Driver")
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


# Test 5: Missing inventory (no car) blocks registration
def test_inventory_required_for_registration():
    """A team without a car in inventory cannot complete registration."""
    team = Team("Delta Team")
    team.register_member("Mike Driver")
    team.assign_team_role("Mike Driver", "Driver")
    # No car added -> should fail

    with pytest.raises(RuntimeError):
        team.complete_registration()


# Test 6: Mission requiring Mechanic fails if no Mechanic on team
def test_mission_missing_required_role():
    """A rescue mission requires both Driver and Mechanic roles (Business Rule 5)."""
    team = Team("Echo Team")
    team.register_member("Sam Driver")
    team.assign_team_role("Sam Driver", "Driver")
    team.inventory.add_car("Rescue Van")
    team.complete_registration()
    
    mission = MissionControl("Rescue Op", mission_type="rescue")
    
    with pytest.raises(RuntimeError, match="missing this role"):
        mission.add_team(team)


# Test 7: Damaged car mission requires mechanic check (Business Rule 3)
def test_damaged_car_requires_mechanic():
    """If a car is damaged, a mission must verify a Mechanic is available."""
    team = Team("Repair Crew")
    team.register_member("Ace Racer")
    team.assign_team_role("Ace Racer", "Driver")
    # No mechanic added — can't do a mission if car is damaged
    team.inventory.add_car("Damaged Car")
    team.complete_registration()
    team.inventory.cars[0]["is_damaged"] = True  # simulate damage AFTER registration

    mission = MissionControl("Emergency Repair", mission_type="delivery")

    # Business Rule 3: Requires Mechanic to proceed because of damaged car
    with pytest.raises(RuntimeError, match="requires a Mechanic to proceed"):
        mission.add_team(team)


# Test 8: A crew member must be registered before role assignment (Business Rule 1)
def test_crew_must_register_before_role():
    """Business Rule 1: A crew member must be registered before a role can be assigned."""
    team = Team("Strict Crew")
    # Trying to assign a role to someone not registered
    with pytest.raises(ValueError, match="is not registered. Register first"):
        team.assign_team_role("Ghost", "Driver")


# Test 9: Registered team with no Driver cannot race (Business Rule 2)
def test_no_driver_cannot_race():
    """Business Rule 2: Only crew members with the Driver role may enter a race."""
    team = Team("Mechanics Only")
    team.register_member("Bob Wrench")
    team.assign_team_role("Bob Wrench", "Mechanic", skill_level=4)
    team.inventory.add_car("ToolVan")
    
    # We must force bypass the registration block to test the race.py check directly
    team.register_member("Temp Driver")
    team.assign_team_role("Temp Driver", "Driver")
    team.complete_registration()
    
    # Now remove the driver to simulate the edge case for race.py
    team.roster.members = [m for m in team.roster.members if m.role != "Driver"]

    race = Race("Street Circuit", 2)
    with pytest.raises(ValueError, match="no Driver in crew"):
        race.run_race(team)


# Test 10: Multi-team leaderboard sorting (Results + Leaderboard Integration)
def test_multi_team_leaderboard_sorting():
    """Verify Results module correctly sorts multiple teams and updates Leaderboard in exact 1st/2nd/3rd order."""
    t1 = make_ready_team("Team Slow")
    t2 = make_ready_team("Team Fast")
    t3 = make_ready_team("Team Medium")

    data = [
        {"team_id": t1.team_id, "status": "Completed", "time": 90, "prize": 1000, "team": t1},  # 3rd
        {"team_id": t2.team_id, "status": "Completed", "time": 40, "prize": 1000, "team": t2},  # 1st
        {"team_id": t3.team_id, "status": "Completed", "time": 60, "prize": 1000, "team": t3},  # 2nd
    ]

    processor = RaceResultProcessor(data)
    processor.calculate_points()

    # Fast gets 10 points, Medium gets 5, Slow gets 2
    top_teams = global_leaderboard.get_top_teams(3)
    assert top_teams[0][0] == t2.team_id
    assert top_teams[0][1] == 10
    assert top_teams[1][0] == t3.team_id
    assert top_teams[1][1] == 5
    assert top_teams[2][0] == t1.team_id
    assert top_teams[2][1] == 2


# Test 11: Earning prize money and spending it on Inventory (Race + Results + Inventory Integration)
def test_earn_prize_and_buy_tools():
    """Verify a team can win a race and immediately use the prize money to buy tools via Inventory deduct_cash."""
    team = make_ready_team("Spenders")
    initial_cash = team.inventory.cash_balance  # Should be 5000 base

    # Run a high difficulty race to earn lots of money
    race = Race("Highroller Track", 5) # difficulty 5 -> prize 5000
    res = race.run_race(team)
    processor = RaceResultProcessor([res])
    processor.calculate_points() # Team gets 1st place -> 100% of 5000 = 5000 added
    
    assert team.inventory.cash_balance == initial_cash + 5000

    # Buying expensive parts (Integration check on Inventory deduction)
    success = team.inventory.deduct_cash(7000)
    assert success is True
    team.inventory.add_part("Turbocharger", 1)
    
    assert team.inventory.cash_balance == (initial_cash + 5000) - 7000


# Test 12: Mission rejected if Crew Roster is totally full but missing specific role
def test_mission_rejected_roster_full_but_missing_role():
    """Verify that even a maxed out crew of 8 members fails mission planning if the specific role isn't present."""
    team = Team("Max Roster")
    for i in range(7):
        team.register_member(f"Mechanic {i}")
        team.assign_team_role(f"Mechanic {i}", "Mechanic")
    
    # 8th member is a driver so we can race/register
    team.register_member("Only Driver")
    team.assign_team_role("Only Driver", "Driver")
    
    team.inventory.add_car("Clown Car")
    team.complete_registration()

    # Roster is now full (8 members). Mission requires a "Strategist".
    mission = MissionControl("Recon Op", mission_type="recon") # recon requires Strategist
    
    with pytest.raises(RuntimeError, match="requires a Strategist"):
        mission.add_team(team)
