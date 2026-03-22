"""Crew management module for StreetRace Manager.
Manages crew members, their roles, and skill levels.
"""
from integration.code.utils import validate_string

# Assignment-required roles for street racing
VALID_ROLES = ["Driver", "Mechanic", "Strategist", "Navigator"]


class CrewMember:
    """Represents a single crew member with a role and skill level."""

    def __init__(self, name, role=None, skill_level=1):
        if not validate_string(name):
            raise ValueError("Invalid crew name.")
        if role is not None and role not in VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of {VALID_ROLES}")
        if not (1 <= skill_level <= 5):
            raise ValueError("Skill level must be between 1 and 5.")

        self.name = name
        self.role = role
        self.skill_level = skill_level
        self.is_ready = True

    def assign_role(self, role):
        """Assign or reassign a role to the crew member."""
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of {VALID_ROLES}")
        self.role = role

    def is_driver(self):
        """Return True if this crew member is a Driver."""
        return self.role == "Driver"


class CrewRoster:
    """Manages the full list of crew members for a team."""

    def __init__(self):
        self.members = []

    def add_member(self, name):
        """Add a new member to the roster (without a role)."""
        if len(self.members) >= 8:
            raise OverflowError("Crew roster is full (max 8).")
        member = CrewMember(name, role=None)
        self.members.append(member)
        return member

    def assign_role_to_member(self, name, role, skill_level=1):
        """Assign a role to an already registered member."""
        for m in self.members:
            if m.name == name:
                m.assign_role(role)
                m.skill_level = skill_level
                return m
        raise ValueError(f"Member {name} is not registered. Register first.")

    def get_drivers(self):
        """Return all members with the Driver role."""
        return [m for m in self.members if m.is_driver()]

    def get_mechanics(self):
        """Return all members with the Mechanic role."""
        return [m for m in self.members if m.role == "Mechanic"]

    def has_role(self, role):
        """Return True if at least one member has the given role."""
        return any(m.role == role for m in self.members)

    def is_complete(self):
        """A crew is complete if it has at least 1 Driver registered."""
        return self.has_role("Driver")
