"""Inventory management module."""

class Inventory:
    def __init__(self, fuel_capacity=1000):
        self.fuel = fuel_capacity
        self.parts = {}
        
    def add_part(self, part_name, quantity=1):
        """Add parts to ship inventory."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        self.parts[part_name] = self.parts.get(part_name, 0) + quantity

    def consume_fuel(self, amount):
        """Consume fuel for travel."""
        if amount > self.fuel:
            return False
        self.fuel -= amount
        return True

    def is_prepared(self):
        """Check if inventory has minimum requirements for a race."""
        return self.fuel >= 500 and "Engine Core" in self.parts
