from typing import Dict, Any, List, Tuple

class TrafficService:
    @staticmethod
    def calculate_density(vehicle_count: int, avg_speed_kmh: float, road_capacity: int = 50) -> Tuple[int, str]:
        """
        Calculate traffic density percentage and category level.
        Density = f(vehicle_count, avg_speed, road_capacity)
        """
        speed_factor = max(0.1, min(1.0, (60.0 - avg_speed_kmh) / 60.0))
        volume_factor = min(1.0, vehicle_count / float(road_capacity))

        # Combined density index (0 - 100%)
        density_val = int((volume_factor * 0.6 + speed_factor * 0.4) * 100)
        density_val = max(5, min(99, density_val))

        if density_val >= 80 or (avg_speed_kmh < 12 and vehicle_count > 30):
            return density_val, "SEVERE"
        elif density_val >= 60 or avg_speed_kmh < 20:
            return density_val, "HIGH"
        elif density_val >= 35:
            return density_val, "MEDIUM"
        else:
            return density_val, "LOW"

    @staticmethod
    def calculate_vehicle_distribution(total_vehicles: int) -> Dict[str, int]:
        """Realistic urban traffic distribution breakdown."""
        cars = int(total_vehicles * 0.45)
        bikes = int(total_vehicles * 0.28)
        autos = int(total_vehicles * 0.12)
        buses = int(total_vehicles * 0.08)
        trucks = max(0, total_vehicles - (cars + bikes + autos + buses))
        return {
            "cars": cars,
            "motorcycles": bikes,
            "auto_rickshaws": autos,
            "buses": buses,
            "trucks": trucks
        }
