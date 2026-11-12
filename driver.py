import random


def calculate_target_spec(seg_max_speed, driver_factor):
    """
    seg_max_speed - OSRM speed in m/s
    returns the goal speed in m/s
    """
    variation = random.uniform(0.95, 1.05)

    factor = driver_factor * variation

    factor = min(factor, 1.125)

    return seg_max_speed * factor


def step_speed(current, target, max_acceleration, max_deceleration, dt):
    """Returns the new speed in m/s after dt seconds."""
    # todo - move the accelerate/decelerate logic from the commented block in main.py
    raise NotImplementedError
