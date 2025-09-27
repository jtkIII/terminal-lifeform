import random
import time

from tqdm import tqdm


def pause_simulation(r: int, desc: str = "Pausing Simulation", delay: float = 0.01):
    for _ in tqdm(range(r), desc=desc):
        time.sleep(delay)  # simulate time passing


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between a minimum and maximum."""
    return max(min_value, min(value, max_value))


def passive_aggressive_threshold(aggressiveness: float) -> float:
    """Calculate the threshold for passive vs aggressive behavior."""
    return clamp(0.5 + (aggressiveness - 0.5) * 2, 0.0, 1.0)


def time_passes(delay: float = 0.01):
    """Simulate time passing with a short delay."""
    if random.random() < 0.1:  # 10% chance to pause
        time.sleep(delay)  # simulate time passing
