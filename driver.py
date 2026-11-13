import random


def calculate_target_speed(seg_max_speed, driver_factor):
    """
    seg_max_speed - OSRM speed in m/s
    returns the goal speed in m/s
    """
    variation = random.uniform(0.95, 1.05)

    factor = driver_factor * variation

    factor = min(factor, 1.125)

    return seg_max_speed * factor


def step_speed(current, target, max_acceleration, max_deceleration, tick):
    """Returns the new speed in m/s after `tick` seconds."""
    if current < target:
        current = min(current + max_acceleration * tick, target)
    elif current > target:
        current = max(current - max_deceleration * tick, target)

    return current
