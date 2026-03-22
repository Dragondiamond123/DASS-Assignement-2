"""Registration module for StreetRace Manager.
Registers new crew members, storing their name and role.
"""
from integration.code.utils import generate_id, validate_string
from integration.code.crew import CrewRoster
from integration.code.inventory import Inventory


class Team:
    """Represents a racing team with crew and inventory."""

    def __init__(self, team_name):
        if not validate_string(team_name, min_length=3):
            raise ValueError("Team name must be at least 3 characters.")

        self.team_id = generate_id("TEAM")
        self.name = team_name
        self.roster = CrewRoster()     # Integration with crew.py
        self.inventory = Inventory()   # Integration with inventory.py
        self.is_registered = False

    def register_member(self, name):
        """Register a new crew member onto this team's roster without a role."""
        # Business Rule 1: A crew member must be registered before role is assigned
        return self.roster.add_member(name)

    def assign_team_role(self, name, role, skill_level=1):
        """Assign a role to a registered crew member."""
        return self.roster.assign_role_to_member(name, role, skill_level)

    def complete_registration(self):
        """
        Verify the team has at least one Driver (mandatory for races)
        and minimum inventory before officially registering them.
        """
        # Business Rule 1: A crew member must be registered before role is assigned
        if not self.roster.is_complete():
            raise RuntimeError("Cannot register: Team needs at least one Driver.")
        # Business Rule: Must have at least 1 car to race
        if not self.inventory.is_prepared():
            raise RuntimeError("Cannot register: No car available in inventory.")

        self.is_registered = True
        return self.team_id
