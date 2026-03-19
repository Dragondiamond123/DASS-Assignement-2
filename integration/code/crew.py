"""Crew management module."""
from integration.code.utils import validate_string

VALID_ROLES = ["Pilot", "Engineer", "Navigator", "Captain"]

class CrewMember:
    def __init__(self, name, role):
        if not validate_string(name):
            raise ValueError("Invalid crew name.")
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of {VALID_ROLES}")
        
        self.name = name
        self.role = role
        self.is_ready = True

class CrewRoster:
    def __init__(self):
        self.members = []

    def add_member(self, name, role):
        """Add a new member to the roster."""
        if len(self.members) >= 4:
            raise OverflowError("Crew roster is full (max 4).")
        member = CrewMember(name, role)
        self.members.append(member)
        return member

    def is_complete(self):
        """A crew is complete if it has at least 2 members and a Pilot."""
        has_pilot = any(m.role == "Pilot" for m in self.members)
        return len(self.members) >= 2 and has_pilot
