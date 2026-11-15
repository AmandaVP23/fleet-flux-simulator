import random


DEFAULT_DRIVER_FACTOR = 1.0


def get_driver_factor(driver_id):
    """
    Stable per-driver multiplier on the segment speed (<1 cautious, >1 aggressive).
    Seeded by driver_id so the same driver behaves the same on every route and
    across restarts. No driver assigned -> neutral factor.
    """
    if driver_id is None:
        return DEFAULT_DRIVER_FACTOR
    return random.Random(driver_id).triangular(0.85, 1.15, 1.0)


def calculate_target_speed(seg_max_speed, driver_factor, vehicle_max_speed):
    """
    seg_max_speed - OSRM speed in m/s
    vehicle_max_speed - cap from the vehicle profile in m/s
    returns the goal speed in m/s
    """
    variation = random.uniform(0.95, 1.05)

    factor = driver_factor * variation

    factor = min(factor, 1.125)

    return min(seg_max_speed * factor, vehicle_max_speed)


def step_speed(current, target, max_acceleration, max_deceleration, tick):
    """Returns the new speed in m/s after `tick` seconds."""
    if current < target:
        current = min(current + max_acceleration * tick, target)
    elif current > target:
        current = max(current - max_deceleration * tick, target)

    return current
