"""
File: entity_utils.py
Author: Jtk III
Date: 2024-06-10
Description: Utility functions for entity state calculations.
"""

from entity import Entity


def calc_energy_change(entity: Entity, environment_factors: dict) -> float:
    """
    Calculates net energy change from consumption and gain from environment.
    """

    # Metabolism cost (base + health penalty)
    energy_consumed = entity.parameters["metabolism_rate"]

    if entity.health < 50.0:
        energy_consumed += (50.0 - entity.health) * 0.1

    # Energy gain from environment (e.g., food intake)
    resource_availability = environment_factors.get("resource_availability", 1.0)
    foraging_efficiency = entity.parameters.get("foraging_efficiency", 1.0)

    energy_gained = resource_availability * foraging_efficiency * 1.8  # scale as needed

    # Starvation penalty (inefficiency when resources are low)
    if resource_availability < 1.0:
        energy_consumed += (1.0 - resource_availability) * 5.0

    return energy_gained - energy_consumed


def calc_health_change(entity: Entity, environment_factors: dict) -> float:
    energy = entity.energy
    temperature = environment_factors.get("temperature", 25.0)
    pollution = environment_factors.get("pollution", 0.0)
    radiation = environment_factors.get("radiation_background", 0.0)
    recovery = entity.parameters["health_recovery_rate"]
    decay = entity.parameters["health_decay_rate"]
    resilience = entity.parameters["resilience"]
    death_rate = environment_factors.get("death_rate", 1.33)

    health_change = -0.005  # Base decay

    if radiation > 0.2:
        decay += (
            (radiation - 0.2) * (1.5 - resilience) * 0.5
        )  # Radiation increases decay

    if entity.health >= 95.0:
        return health_change  # No more gain; just base decay

    # Energy effect
    if energy > 50.0:
        health_change += (energy - 50.0) * recovery * 0.1
    else:
        health_change -= (50.0 - energy) * decay * 0.1

    # Temperature penalty
    if temperature < 10.0 or temperature > 35.0:
        temp_penalty = abs(temperature - 22.5) * (1.0 - resilience) * 0.1
        health_change -= temp_penalty

    # Pollution penalty
    if pollution > 0.1:
        pollution_penalty = pollution * (1.3 - resilience) * 3.0
        health_change -= pollution_penalty

    # Finally just age-related decay
    health_change -= 0.5 * (entity.age**death_rate)  # Exponential decay with age

    # Uncomment the line below for a linear decay with age
    # health_change -= entity.age * 0.01  # Linear decay with age stable

    return health_change


def validate_entity_params(params: dict):
    required_keys = [
        "metabolism_rate",
        "health_recovery_rate",
        "health_decay_rate",
        "resilience",
        "foraging_efficiency",
        "reproduction_chance",
        "aggression",
        "cooperation",
    ]
    missing = [k for k in required_keys if k not in params]
    if missing:
        raise ValueError(f"Missing entity parameters: {missing}")


# filepath: /home/jtk/Dev/TerminalLifeform/src/utils/entity_utils.py
