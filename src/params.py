# filepath: /home/jtk/Dev/TerminalLifeform/src/params.py
import random

default_environment_factors = {
    "resource_availability": 1.0,  # 0.0 (scarce) to 1.0 (abundant)
    "temperature": 25.0,  # Temperature in Celsius
    "pollution": 0.1,  # 0.0 (clean) to 1.0 (polluted)
    "event_chance": 0.03,  # Chance of a random event per step
    "interaction_strength": 0.5,  # Base strength of entity interactions
    "mutation_rate": 0.11,  # Probability of a parameter mutating (0.0 to 1.0)
    "mutation_strength": 0.03,  # (3%)
    "predator_chance": random.uniform(0.1, 0.2),  # Chance of a predator event
    "predator_threshold": 250,  # Population threshold to trigger predator event
    "predator_impact_percentage": 0.13,  # Percentage of population removed by predator
    # NOT YET IMPLEMENTED:
    "resource_regeneration_rate": random.uniform(
        0.1, 0.9
    ),  # Rate at which resources regenerate
    "seasonal_variation": 0.0,  # Amplitude of seasonal changes (0.0 to 1.0)
    # if population > X, trigger a rare catastrophic event (mass die-off, meteor, plague).
    "catastrophe_threshold": 0.0,  # Population threshold for natural disasters
    "radiation_background": 0.0,  # Background radiation level affecting mutation (0.0 to 1.0)
    "disaster_chance": 0.0,  # Chance of a natural disaster occurring
    "disaster_impact": 0.0,  # Percentage of population affected by disaster
    "growth_rate": 1.0,  # Base growth rate modifier
    "death_rate": 1.0,  # Base death rate modifier
    "competition_intensity": 0.5,  # Intensity of competition for resources
    # Soft population cap. Growth slows or reverses as total entities approach this.
    "carrying_capacity": 1000,
    "prosperity_threshold": 200,  # Above this, reproduction is more efficient
    "prosperity_boost": 1.3,  # Growth multiplier if above threshold
}

# Override with specific simulation parameters
# override_params = {
#     # "temperature": 20.0,
#     # "pollution": 0.1,
#     # "event_chance": 0.03,
#     # "interaction_strength": 0.3,
#     # "mutation_rate": 0.13,
#     # "mutation_strength": 0.13,
#     # "predator_chance": 0.13,
#     # "predator_threshold": 1200,
#     "predator_impact_percentage": 0.1,  # 1% of population removed by predator
# }

entity_params = {
    "max_age": 99,
    "initial_health": 100.0,
    "initial_energy": 100.0,
    "metabolism_rate": 0.3,
    "health_recovery_rate": 1.15,
    "health_decay_rate": 1.35,
    "resilience": 0.18,
    "foraging_efficiency": 0.35,
    "thriving_threshold_health": 65.0,
    "thriving_threshold_energy": 60.0,
    "struggling_threshold_health": 33.0,
    "struggling_threshold_energy": 22.0,
    "reproduction_chance": 1.3,
    "min_reproduction_age": 13,
    "aggression": 0.3,
    "cooperation": 0.1,
}

# hardy_entity_params = {
#     "max_age": 111,
#     "resilience": 0.31,
#     "foraging_efficiency": 0.55,
#     "metabolism_rate": 0.3,
#     "reproduction_chance": 0.25,
#     "aggression": 0.25,
# }

# random_parameters = {
#     "max_age": random.randint(55, 135),
#     "metabolism_rate": random.uniform(0.1, 1.0),
#     "foraging_efficiency": random.uniform(0.35, 1.0),
#     "resilience": random.uniform(0.0, 1.0),
#     "reproduction_chance": random.uniform(0.05, 0.3),
#     "aggression": random.uniform(0.0, 1.0),
# }

# max_parameters = {
#     "max_age": 135,
#     "metabolism_rate": 1.0,
#     "foraging_efficiency": 1.0,
#     "resilience": 1.0,
#     "reproduction_chance": 0.5,
#     "aggression": 1.0,
# }
