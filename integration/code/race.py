"""Race Management module for StreetRace Manager.
Creates races and selects appropriate drivers and cars from the system.
"""
import random


class Race:
    """Manages a single race event."""

    def __init__(self, track_name, difficulty):
        self.track_name = track_name
        self.difficulty = difficulty  # 1 (Easy) to 5 (Hard)
        self.prize_money = difficulty * 1000  # Higher difficulty = more prize

    def run_race(self, team):
        """
        Simulate a race for a registered Team.
        Business Rule 2: Only crew members with the Driver role may enter a race.
        Returns a raw result dict with status, time, and prize.
        """
        if not team.is_registered:
            raise ValueError("Team is not officially registered for racing!")

        # Business Rule 2: Only Drivers may race
        drivers = team.roster.get_drivers()
        if not drivers:
            raise ValueError("Cannot race: Team has no Driver in crew!")

        # Pick a ready car
        ready_cars = team.inventory.get_ready_cars()
        if not ready_cars:
            raise ValueError("Cannot race: Team has no ready cars!")
        car = ready_cars[0]

        # Driver skill affects performance
        avg_skill = sum(d.skill_level for d in drivers) / len(drivers)
        efficiency = avg_skill * 10

        # Calculate race time
        base_time = self.difficulty * 100
        completion_time = base_time - efficiency + random.randint(0, 50)

        # 30% chance for the car to get damaged during the race
        if random.random() < 0.3:
            car["is_damaged"] = True

        return {
            "team_id": team.team_id,
            "team": team,
            "status": "Completed",
            "time": completion_time,
            "prize": self.prize_money
        }
