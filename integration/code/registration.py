"""Team registration module."""
from integration.code.utils import generate_id, validate_string
from integration.code.crew import CrewRoster
from integration.code.inventory import Inventory

class Team:
    def __init__(self, team_name):
        if not validate_string(team_name, min_length=3):
            raise ValueError("Team name must be at least 3 characters.")
        
        self.team_id = generate_id("TEAM")
        self.name = team_name
        self.roster = CrewRoster()     # Integration with crew.py
        self.inventory = Inventory()   # Integration with inventory.py
        self.is_registered = False

    def complete_registration(self):
        """
        Verify the team has a valid crew and minimum inventory 
        before officially registering them for a race.
        """
        if not self.roster.is_complete():
            raise RuntimeError("Cannot register: Crew is incomplete.")
        if not self.inventory.is_prepared():
            raise RuntimeError("Cannot register: Inventory is not prepared.")
        
        self.is_registered = True
        return self.team_id
