"""
File: entity_utils.py
Author: Jtk III
Date: 2024-06-10
Description: Utility functions for entity state calculations.
"""

import random

from entity import Entity
from utils.logging_config import setup_logger

# from utils.utils import pause_simulation, time_passes

logger = setup_logger(__name__)


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


def add_entity(sim, entity: Entity):
    validate_entity_params(entity.parameters)
    sim.entities.append(entity)
    sim.total_entities += 1
    logger.info(f"Added new entity: {entity.id}: {entity.name}")


def process_entity(sim, entity: Entity):
    """
    Applies all updates to a single entity for the current Epoch.
    """

    if not entity.is_alive():
        return  # Skip dead entities

    for entity in sim.entities:  # Update entity's environmental memory
        condition = sim.environment_factors["resource_availability"] - 0.5
        # Positive if abundant, negative if scarce
        entity.environment_memory.append(condition)
        if len(entity.environment_memory) > entity.memory_span:
            entity.environment_memory.pop(0)

    entity.age += 1
    energy_change = calc_energy_change(entity, sim.environment_factors)
    entity.energy = max(0.0, min(100.0, entity.energy + energy_change))
    health_change = calc_health_change(entity, sim.environment_factors)
    entity.health = max(0.0, min(100.0, entity.health + health_change))
    entity.update_status()


def adapt_entities(sim):
    """
    Adjust entity traits based on environmental history.
    Resets memory on significant mutation to simulate evolutionary leaps.
    """
    for entity in sim.entities:
        if not entity.is_alive():
            continue

        # Initialize memory-related attributes if missing
        if not hasattr(entity, "environment_memory"):
            entity.environment_memory = []
        if not hasattr(entity, "memory_span"):
            entity.memory_span = 20

        # Record current environment condition relative to baseline
        condition = sim.environment_factors["resource_availability"] - 0.5
        entity.environment_memory.append(condition)
        if len(entity.environment_memory) > entity.memory_span:
            entity.environment_memory.pop(0)

        avg_condition = sum(entity.environment_memory) / len(entity.environment_memory)

        # --- 1. Phenotypic adaptation (within lifetime) ---
        if avg_condition < -0.1:
            # Scarcity = survival traits
            entity.resilience *= 1.02
            entity.metabolism_rate *= 0.97
            entity.reproduction_chance *= 0.93
        elif avg_condition > 0.1:
            # Abundance = growth traits
            entity.resilience *= 0.97
            entity.metabolism_rate *= 1.03
            entity.reproduction_chance *= 1.07

        # --- 2. Small random drift ---
        drift = random.uniform(0.98, 1.02)
        entity.resilience *= drift
        entity.metabolism_rate *= drift
        entity.reproduction_chance *= drift

        # --- 3. Mutation events (evolutionary leaps) ---
        if random.random() < sim.environment_factors.get("mutation_rate", 0.05) * 0.1:
            # Reset memory on big mutation — the entity 'forgets' old pressures
            entity.environment_memory.clear()

            # Big changes (±20%) — this simulates evolution, not just plasticity
            mutation_factor = random.uniform(0.8, 1.2)
            entity.resilience *= mutation_factor
            entity.metabolism_rate *= mutation_factor
            entity.reproduction_chance *= mutation_factor

        # --- 4. Clamp to avoid runaway traits ---
        entity.resilience = max(0.1, min(entity.resilience, 5.0))
        entity.metabolism_rate = max(0.1, min(entity.metabolism_rate, 5.0))
        entity.reproduction_chance = max(0.001, min(entity.reproduction_chance, 2.0))


# filepath: /home/jtk/Dev/TerminalLifeform/src/utils/entity_utils.py
