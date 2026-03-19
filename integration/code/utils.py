"""Utility functions for StreetRace Manager."""
import uuid

def generate_id(prefix="ID"):
    """Generate a unique identifier."""
    return f"{prefix}-{str(uuid.uuid4())[:8].upper()}"

def validate_string(text, min_length=2):
    """Validate that a string is not empty and meets minimum length."""
    if not isinstance(text, str):
        return False
    return len(text.strip()) >= min_length
