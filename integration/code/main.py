"""StreetRace Manager - Command Line Interface"""
import sys
from integration.code.registration import Team
from integration.code.mission import MissionControl
from integration.code.race import Race

def main():
    print("========================================")
    print("Welcome to StreetRace Manager System CLI")
    print("========================================")
    
    print("\n[1] Registering a new Racing Team...")
    team = Team("Midnight Runners")
    
    print("[2] Adding Crew Members...")
    team.register_member("Dom Toretto")
    team.assign_team_role("Dom Toretto", "Driver", skill_level=5)
    print(" -> Added Dom Toretto (Driver)")
    
    team.register_member("Letty Ortiz")
    team.assign_team_role("Letty Ortiz", "Mechanic", skill_level=4)
    print(" -> Added Letty Ortiz (Mechanic)")
    
    print("[3] Adding Inventory...")
    team.inventory.add_car("Dodge Charger 1970")
    print(" -> Added Dodge Charger 1970")
    
    team.complete_registration()
    print("\n>>> Team 'Midnight Runners' Registration Complete! <<<\n")
    
    print("[4] Initializing Underground Race Mission...")
    mission = MissionControl("Quarter Mile Sprint", mission_type="delivery")
    mission.add_team(team)
    
    print("[5] Creating Track Event...")
    track = Race("LA River Basin", difficulty=3)
    mission.add_race(track)
    
    print("\n[6] Executing Mission...")
    standings = mission.execute_mission()
    
    print("\n========================================")
    print("RACE RESULTS & GLOBAL LEADERBOARD")
    print("========================================")
    for rank, (team_id, points) in enumerate(standings, 1):
        print(f"{rank}. Team ID: {team_id} | Points: {points}")
    print("========================================")
    
    print(f"Final Inventory Cash Balance: ${team.inventory.cash_balance}")

if __name__ == "__main__":
    main()
