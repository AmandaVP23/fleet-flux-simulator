import random

# max_speed in m/s, accel in m/s², decel is (low, high, mode) for random.triangular
VEHICLE_PROFILES = {
    "CAR":     {"max_speed": 36, "accel": 2.0, "decel": (2.0, 4.0, 3.0)},
    "VAN":     {"max_speed": 31, "accel": 1.5, "decel": (1.8, 3.5, 2.5)},
    "TRUCK":   {"max_speed": 25, "accel": 0.8, "decel": (1.2, 2.5, 1.8)},
    "TRAILER": {"max_speed": 22, "accel": 0.5, "decel": (1.0, 2.0, 1.5)},
}
DEFAULT_TYPE = "CAR"


def get_profile(vehicle_type):
    """Returns the physical limits for a vehicle type."""
    base = VEHICLE_PROFILES.get(vehicle_type, VEHICLE_PROFILES[DEFAULT_TYPE])
    low, high, mode = base["decel"]
    return {
        "max_speed": base["max_speed"],
        "max_acceleration": base["accel"],
        "max_deceleration": random.triangular(low, high, mode),
    }
