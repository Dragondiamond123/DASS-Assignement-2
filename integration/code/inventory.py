"""Inventory module for StreetRace Manager.
Tracks cars, spare parts, tools, and cash balance.
"""


class Inventory:
    """Tracks all physical and financial resources of a team."""

    def __init__(self, starting_cash=5000):
        self.cash_balance = starting_cash   # Assignment: cash balance tracked
        self.cars = []
        self.spare_parts = {}
        self.tools = {}

    def add_car(self, car_name):
        """Register a car to the team inventory."""
        self.cars.append(car_name)

    def add_part(self, part_name, quantity=1):
        """Add spare parts to the inventory."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        self.spare_parts[part_name] = self.spare_parts.get(part_name, 0) + quantity

    def add_tool(self, tool_name, quantity=1):
        """Add tools to the inventory."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        self.tools[tool_name] = self.tools.get(tool_name, 0) + quantity

    def add_prize_money(self, amount):
        """Add prize money to cash balance after a race result."""
        if amount < 0:
            raise ValueError("Prize money must not be negative.")
        self.cash_balance += amount

    def deduct_cash(self, amount):
        """Deduct cash for expenses. Returns False if insufficient funds."""
        if amount > self.cash_balance:
            return False
        self.cash_balance -= amount
        return True

    def is_prepared(self):
        """Check if team has minimum resources: at least 1 car and some cash."""
        return len(self.cars) >= 1 and self.cash_balance >= 0
