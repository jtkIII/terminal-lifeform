"""
File: world_loader.py
Author: Jtk III
Date: 2024-06-10
Description: Load and manage world presets for the simulation.
"""

import random
from copy import deepcopy


def list_worlds() -> list[str]:
    """Return a list of all available world preset names."""
    add_mutant_worlds()  # Ensure mutant worlds are added
    return list(WORLD_PRESETS.keys())


def load_world(name: str = "default") -> dict:
    print(f"\n🚀 Launching Terminal Lifeform using {name}\n")
    if name not in WORLD_PRESETS:
        print(f"[WARN] Unknown world '{name}', falling back to 'default'.")
        name = "default"
    return deepcopy(WORLD_PRESETS[name])


def evolve_world(base: str, changes: dict) -> dict:
    world = deepcopy(WORLD_PRESETS[base])
    world.update(changes)
    return world


def describe_world(name: str) -> str:
    """Return a human-readable description of a world preset."""
    try:
        preset = WORLD_PRESETS[name]
    except KeyError:
        raise ValueError(f"Unknown world preset: {name}")  # noqa: B904
    return f"{preset['name']}: {preset['description']}"


def add_mutant_worlds():
    """Add mutant world presets with extreme mutation rates."""
    mutant = evolve_world(
        "garden_world",
        {
            "mutation_rate": 0.5,
            "mutation_strength": 0.1,
            "event_chance": 0.05,
            "disaster_chance": 0.02,
            "disaster_impact": 0.1,
            "resource_availability": 1.33,
            "resource_regeneration_rate": 0.6,
            "carrying_capacity": 3333,
            "growth_rate": 1.33,
            "death_rate": 1.0,
            "competition_intensity": 0.4,
        },
    )
    chaotic_mutant = evolve_world(
        "chaotic_world",
        {
            "mutation_rate": 0.7,
            "mutation_strength": 0.2,
            "event_chance": 0.2,
            "disaster_chance": 0.15,
            "disaster_impact": 0.5,
            "resource_availability": 0.7,
            "resource_regeneration_rate": 0.3,
            "carrying_capacity": 400,
            "growth_rate": 0.9,
            "death_rate": 1.25,
            "competition_intensity": 0.9,
        },
    )
    WORLD_PRESETS["mutant_garden_world"] = mutant
    WORLD_PRESETS["mutant_chaotic_world"] = chaotic_mutant  # More extreme chaos


def choose_world() -> str:
    """Prompt the user to choose a world preset interactively with descriptions and a random option."""
    worlds = list_worlds()

    print("\n🌍 Available Worlds:\n")
    for idx, name in enumerate(worlds, start=1):
        preset = WORLD_PRESETS[name]
        icon = preset.get("icon", "")
        desc = preset.get("description", "No description provided.")
        print(f"{idx:<2} {icon:<5} {name:<5} — {desc}")

    print("\n0. 🎲 Random World — Choose a random preset from the list above")

    while True:
        choice = input("\nEnter the number of the world you want to run: ").strip()
        if choice.isdigit():
            choice_int = int(choice)
            if choice_int == 0:
                return random.choice(worlds)
            if 1 <= choice_int <= len(worlds):
                return worlds[choice_int - 1]
        print("❌ Invalid choice. Please enter a valid number.")


WORLD_PRESETS = {
    "default": {
        "name": "Default World",
        "description": "Balanced simulation with moderate conditions and average dynamics. Not adaptive.",
        "icon": "🌍",
        "resource_availability": 1.0,
        "temperature": 25.0,
        "pollution": 0.1,
        "event_chance": 0.03,
        "interaction_strength": 0.5,
        "mutation_rate": 0.1,
        "mutation_strength": 0.01,
        "predator_chance": 0.1,
        "predator_threshold": 350,
        "predator_impact_percentage": 0.13,
        "resource_regeneration_rate": 0.5,
        "seasonal_variation": 0.2,
        "catastrophe_threshold": 0.0,
        "radiation_background": 0.1,
        "disaster_chance": 0.1,
        "disaster_impact": 0.1,
        "growth_rate": 1.0,
        "death_rate": 1.15,
        "competition_intensity": 0.5,
        "carrying_capacity": 2500,
        "prosperity_threshold": 200,
        "prosperity_boost": 1,
        "optimal_density": 1000,
        "density_efficiency": 0.2,
        "adaptive_environment": False,  # New flag for adaptive behavior notice it's off by default
    },
    "default_adaptive": {
        "name": "Default Adaptive",
        "description": "Balanced simulation with moderate conditions, average dynamics, and adaptive.",
        "icon": "🌍",
        "resource_availability": 1.0,
        "temperature": 25.0,
        "pollution": 0.1,
        "event_chance": 0.03,
        "interaction_strength": 0.5,
        "mutation_rate": 0.1,
        "mutation_strength": 0.01,
        "predator_chance": 0.1,
        "predator_threshold": 350,
        "predator_impact_percentage": 0.13,
        "resource_regeneration_rate": 0.5,
        "seasonal_variation": 0.2,
        "catastrophe_threshold": 0.0,
        "radiation_background": 0.1,
        "disaster_chance": 0.1,
        "disaster_impact": 0.1,
        "growth_rate": 1.0,
        "death_rate": 1.15,
        "competition_intensity": 0.5,
        "carrying_capacity": 2500,
        "prosperity_threshold": 200,
        "prosperity_boost": 1,
        "optimal_density": 1000,
        "density_efficiency": 0.2,
        "adaptive_environment": True,  # Adaptive behavior enabled
        "memory_window": 50,
        "memory_sensitivity": 1.0,  # neutral reaction to trends
    },
    "harsh_world": {
        "name": "Harsh World",
        "description": "A brutal environment with scarce resources and frequent threats.",
        "icon": "🏜️",
        "resource_availability": 0.44,  # low resources
        "temperature": 5.0,  # cold
        "pollution": 0.6,  # higher pollution
        "event_chance": 0.08,
        "interaction_strength": 0.8,
        "mutation_rate": 0.22,
        "mutation_strength": 0.052,
        "predator_chance": 0.25,
        "predator_threshold": 150,
        "predator_impact_percentage": 0.25,
        "resource_regeneration_rate": 0.2,
        "seasonal_variation": 0.6,
        "catastrophe_threshold": 500,
        "radiation_background": 0.2,
        "disaster_chance": 0.05,
        "disaster_impact": 0.4,
        "growth_rate": 0.84,
        "death_rate": 1.4,
        "competition_intensity": 0.9,
        "carrying_capacity": 400,
        "prosperity_threshold": 200,
        "prosperity_boost": 1.3,
        "optimal_density": 800,
        "density_efficiency": 0.2,
    },
    "garden_world": {
        "name": "Garden World",
        "description": "A utopian paradise with abundant resources and minimal dangers.",
        "icon": "🌳",
        "resource_availability": 1.5,
        "temperature": 22.0,
        "pollution": 0.01,
        "event_chance": 0.01,
        "interaction_strength": 0.3,
        "mutation_rate": 0.05,
        "mutation_strength": 0.02,
        "predator_chance": 0.02,
        "predator_threshold": 800,
        "predator_impact_percentage": 0.02,
        "resource_regeneration_rate": 1,
        "seasonal_variation": 0.1,
        "catastrophe_threshold": 0.5,
        "radiation_background": 0.01,
        "disaster_chance": 0.1,
        "disaster_impact": 0.1,
        "growth_rate": 1.5,
        "death_rate": 0.92,
        "competition_intensity": 0.1,
        "carrying_capacity": 3000,
        "prosperity_threshold": 500,
        "prosperity_boost": 1.5,
        "optimal_density": 1000,
        "density_efficiency": 0.35,
        "adaptive_environment": True,
        "memory_window": 80,
        "memory_sensitivity": 0.9,  # slow-ish to overreact
    },
    "chaotic_world": {
        "name": "Chaotic World",
        "description": "Volatile and unpredictable environment with frequent disasters and mutations.",
        "icon": "🌪️",
        "resource_availability": 0.9,
        "temperature": 30.0,
        "pollution": 0.3,
        "event_chance": 0.15,
        "interaction_strength": 0.7,
        "mutation_rate": 0.6,
        "mutation_strength": 0.3,
        "predator_chance": 0.3,
        "predator_threshold": 200,
        "predator_impact_percentage": 0.25,
        "resource_regeneration_rate": 0.4,
        "seasonal_variation": 0.8,
        "catastrophe_threshold": 300,
        "radiation_background": 0.2,
        "disaster_chance": 0.1,
        "disaster_impact": 0.6,
        "growth_rate": 1.0,
        "death_rate": 1.2,
        "competition_intensity": 0.8,
        "carrying_capacity": 500,
        "prosperity_threshold": 200,
        "prosperity_boost": 1.3,
        "optimal_density": 600,
        "density_efficiency": 0.2,
        "adaptive_environment": True,
        "memory_window": 30,
        "memory_sensitivity": 1.2,  # overreacts to trends
    },
    "dunbars_world": {
        "name": "Dunbars World",
        "description": "Cooperation thrives in small groups, but growth beyond ~200 causes rapid collapse.",
        "icon": "👥",
        "resource_availability": 0.9,
        "resource_regeneration_rate": 0.7,
        "temperature": 20.0,
        "pollution": 0.05,
        "seasonal_variation": 0.1,
        "mutation_rate": 0.07,
        "interaction_strength": 0.3,
        "mutation_strength": 0.02,
        "radiation_background": 0.05,
        "event_chance": 0.04,
        "disaster_chance": 0.03,
        "disaster_impact": 0.2,
        "catastrophe_threshold": 300,
        "predator_chance": 0.1,
        "predator_threshold": 220,
        "predator_impact_percentage": 0.15,
        "growth_rate": 0.9,
        "death_rate": 1.0,
        "competition_intensity": 0.7,
        "carrying_capacity": 300,
        "prosperity_threshold": 80,
        "prosperity_boost": 1.4,
        "optimal_density": 150,
        "density_efficiency": 0.35,
    },
    "post_cataclysmic_world": {
        "name": "Post Cataclysmic",
        "description": "Life clings on after mass extinction — low resources, slow recovery, but huge evolutionary leaps.",
        "icon": "🪨",
        "interaction_strength": 0.66,
        "resource_availability": 0.3,
        "resource_regeneration_rate": 0.2,
        "temperature": 10.0,
        "pollution": 0.5,
        "seasonal_variation": 0.3,
        "mutation_rate": 0.25,
        "mutation_strength": 0.06,
        "radiation_background": 0.4,
        "event_chance": 0.02,
        "disaster_chance": 0.05,
        "disaster_impact": 0.6,
        "catastrophe_threshold": 0.0,
        "predator_chance": 0.05,
        "predator_threshold": 100,
        "predator_impact_percentage": 0.1,
        "growth_rate": 0.6,
        "death_rate": 1.1,
        "competition_intensity": 0.4,
        "carrying_capacity": 500,
        "prosperity_threshold": 50,
        "prosperity_boost": 1.6,
        "optimal_density": 200,
        "density_efficiency": 0.25,
        "adaptive_environment": True,
        "memory_window": 50,
        "memory_sensitivity": 1.3,  # overreacts to trends
    },
    "runaway_evolution_world": {
        "name": "Runaway Evolution",
        "description": "Extreme radiation and mutation pressure drive rapid, chaotic evolutionary leaps.",
        "icon": "🧬",
        "resource_availability": 1.0,
        "resource_regeneration_rate": 0.6,
        "temperature": 35.0,
        "pollution": 0.2,
        "seasonal_variation": 0.5,
        "mutation_rate": 0.6,
        "mutation_strength": 0.15,
        "radiation_background": 0.8,
        "event_chance": 0.08,
        "disaster_chance": 0.1,
        "disaster_impact": 0.4,
        "catastrophe_threshold": 800,
        "interaction_strength": 0.6,
        "predator_chance": 0.2,
        "predator_threshold": 500,
        "predator_impact_percentage": 0.2,
        "growth_rate": 1.2,
        "death_rate": 1.3,
        "competition_intensity": 0.8,
        "carrying_capacity": 1500,
        "prosperity_threshold": 300,
        "prosperity_boost": 1.2,
        "optimal_density": 800,
        "density_efficiency": 0.15,
        "adaptive_environment": True,
        "memory_window": 20,
        "memory_sensitivity": 1.5,  # overreacts to trends
    },
    "red_queen_world": {
        # It takes all the running you can do, to keep in the same place.
        "name": "Red Queen World",
        "description": "Intense competition and constant adaptation — evolve or die in an endless arms race.",
        "icon": "👑",
        "resource_availability": 0.7,
        "resource_regeneration_rate": 0.5,
        "temperature": 28.0,
        "pollution": 0.25,
        "seasonal_variation": 0.4,
        "mutation_rate": 0.35,
        "mutation_strength": 0.08,
        "interaction_strength": 0.75,
        "radiation_background": 0.2,
        "event_chance": 0.12,
        "disaster_chance": 0.07,
        "disaster_impact": 0.3,
        "catastrophe_threshold": 400,
        "predator_chance": 0.25,
        "predator_threshold": 250,
        "predator_impact_percentage": 0.2,
        "growth_rate": 1.0,
        "death_rate": 1.3,
        "competition_intensity": 1.0,
        "carrying_capacity": 800,
        "prosperity_threshold": 150,
        "prosperity_boost": 1.25,
        "optimal_density": 400,
        "density_efficiency": 0.25,
        "adaptive_environment": True,
        "memory_window": 40,
        "memory_sensitivity": 1.1,  # mild overreaction
    },
    "golden_world": {
        # https://www.youtube.com/watch?v=hl6JDv4ZG7U
        "name": "Golden World",
        "description": "In this world, everything is governed by the golden ratio, leading to harmonious growth and balance.",
        "icon": "🌟",
        "resource_availability": 1.618,
        "resource_regeneration_rate": 0.618033,
        "temperature": 21.0,
        "pollution": 0.02618033,
        "seasonal_variation": 0.1,
        "mutation_rate": 0.03,
        "mutation_strength": 0.01,
        "interaction_strength": 0.2,
        "radiation_background": 0.01,
        "event_chance": 0.01,
        "disaster_chance": 0.02618033,
        "disaster_impact": 0.055,
        "catastrophe_threshold": 0.11,
        "predator_chance": 0.02618033,
        "predator_threshold": 700,
        "predator_impact_percentage": 0.02,
        "growth_rate": 1.618,
        "death_rate": 1.3,
        "competition_intensity": 0.1,
        "carrying_capacity": 4181,
        "prosperity_threshold": 377,
        "prosperity_boost": 1.618,
        "optimal_density": 1597,
        "density_efficiency": 0.4236067977,
        "adaptive_environment": True,
        "memory_window": 89,
        "memory_sensitivity": 0.8,  # stable, underreacts to trends
    },
    "island_world": {
        # Tell me what you wantin'
        "name": "Island World",
        "description": "Isolated ecosystems with limited resources, leading to unique evolutionary paths and species.",
        "icon": "🏝️",
        "resource_availability": 0.75,
        "resource_regeneration_rate": 0.33,
        "temperature": 24.0,
        "pollution": 0.05,
        "seasonal_variation": 0.3,
        "mutation_rate": 0.15,
        "mutation_strength": 0.04,
        "interaction_strength": 0.4,
        "radiation_background": 0.05,
        "event_chance": 0.05,
        "disaster_chance": 0.04,
        "disaster_impact": 0.25,
        "catastrophe_threshold": 200,
        "predator_chance": 0.15,
        "predator_threshold": 180,
        "predator_impact_percentage": 0.18,
        "growth_rate": 1.3,
        "death_rate": 1.05,
        "competition_intensity": 0.6,
        "carrying_capacity": 1000,
        "prosperity_threshold": 500,
        "prosperity_boost": 1.3,
        "optimal_density": 700,
        "density_efficiency": 0.33,
        "adaptive_environment": True,
        "memory_window": 70,
        "memory_sensitivity": 0.9,  # slightly stable
    },
    "tidal_locked_world": {
        "name": "Tidal Locked",
        "description": "Scorched by day, Frozen in eternal night. Survival thrives on the razor-thin twilight",
        "icon": "🌞",
        "resource_availability": 0.7,
        "resource_regeneration_rate": 0.35,
        "temperature": 50.0,  # Hot average, extremes on both sides
        "pollution": 0.15,
        "seasonal_variation": 0.05,  # Little seasonal change due to locked orbit
        "mutation_rate": 0.18,
        "mutation_strength": 0.05,
        "interaction_strength": 0.8,
        "radiation_background": 0.12,
        "event_chance": 0.04,
        "disaster_chance": 0.06,
        "disaster_impact": 0.25,
        "catastrophe_threshold": 200,
        "predator_chance": 0.2,
        "predator_threshold": 180,
        "predator_impact_percentage": 0.2,
        "growth_rate": 0.95,
        "death_rate": 1.2,
        "competition_intensity": 0.9,
        "carrying_capacity": 500,
        "prosperity_threshold": 150,
        "prosperity_boost": 1.2,
        "optimal_density": 250,
        "density_efficiency": 0.15,
        "adaptive_environment": True,
        "memory_window": 60,
        "memory_sensitivity": 1.0,  # neutral reaction to trends
    },
    "bioengineered_world": {
        "name": "Bioengineered World",
        "description": "Cooperation is rewarded but growth beyond a limit triggers automatic collapse protocols.",
        "icon": "🧪",
        "resource_availability": 1.2,
        "resource_regeneration_rate": 0.8,
        "temperature": 26.0,
        "pollution": 0.02,
        "seasonal_variation": 0.05,
        "mutation_rate": 0.02,  # Artificial stability
        "mutation_strength": 0.005,
        "interaction_strength": 0.4,
        "radiation_background": 0.01,
        "event_chance": 0.02,
        "disaster_chance": 0.01,
        "disaster_impact": 0.1,
        "catastrophe_threshold": 900,
        "predator_chance": 0.05,
        "predator_threshold": 800,
        "predator_impact_percentage": 0.05,
        "growth_rate": 1.2,
        "death_rate": 0.95,
        "competition_intensity": 0.3,
        "carrying_capacity": 1000,
        "prosperity_threshold": 300,
        "prosperity_boost": 1.5,
        "optimal_density": 700,
        "density_efficiency": 0.4,
        "adaptive_environment": True,
        "memory_window": 100,
        "memory_sensitivity": 0.7,  # very stable
    },
    "sentinel_world": {
        "name": "Sentinel World",
        "description": "Life endures under shadow of apocalypse — rare devastating events reset evolution again and again.",
        "icon": "☄️",
        "resource_availability": 1.0,
        "resource_regeneration_rate": 0.6,
        "temperature": 26.0,
        "pollution": 0.2,
        "seasonal_variation": 0.3,
        "mutation_rate": 0.22,
        "mutation_strength": 0.07,
        "interaction_strength": 0.5,
        "radiation_background": 0.3,
        "event_chance": 0.02,
        "disaster_chance": 0.02,  # Very rare...
        "disaster_impact": 0.95,  # ...but nearly total reset
        "catastrophe_threshold": 1000,
        "predator_chance": 0.08,
        "predator_threshold": 400,
        "predator_impact_percentage": 0.15,
        "growth_rate": 0.8,
        "death_rate": 1.1,
        "competition_intensity": 0.5,
        "carrying_capacity": 1200,
        "prosperity_threshold": 180,
        "prosperity_boost": 1.5,
        "optimal_density": 500,
        "density_efficiency": 0.2,
    },
    "entropy_world": {
        "name": "Entropy World",
        "description": "A self-correcting biosphere — abundance sows the seeds of destruction, while collapse nurtures new life.",
        "icon": "🌀",
        "resource_availability": 0.9,
        "resource_regeneration_rate": 0.5,
        "temperature": 25.0,
        "pollution": 0.2,
        "seasonal_variation": 0.4,
        "mutation_rate": 0.25,  # Higher baseline mutation
        "mutation_strength": 0.12,
        "interaction_strength": 0.7,
        "radiation_background": 0.3,
        "event_chance": 0.05,
        "disaster_chance": 0.06,
        "disaster_impact": 0.4,
        "catastrophe_threshold": 500,
        "predator_chance": 0.15,
        "predator_threshold": 300,
        "predator_impact_percentage": 0.2,
        "growth_rate": 1.05,
        "death_rate": 1.05,
        "competition_intensity": 0.8,
        "carrying_capacity": 1000,
        "prosperity_threshold": 200,
        "prosperity_boost": 1.2,
        "optimal_density": 500,
        "density_efficiency": 0.3,
    },
    "inverted_world": {
        "name": "Inverted World",
        "description": "Strength is a liability, scarcity breeds abundance, disasters spark evolution. The Meak shall inherit the Earth.",
        "icon": "🔁",
        "resource_availability": 0.6,
        "resource_regeneration_rate": 0.8,
        "temperature": 22.0,
        "pollution": 0.05,
        "seasonal_variation": 0.2,
        "mutation_rate": 0.4,
        "mutation_strength": 0.15,
        "interaction_strength": 0.9,  # Aggression backfires here
        "radiation_background": 0.1,
        "event_chance": 0.07,
        "disaster_chance": 0.12,  # Frequent, but beneficial in this model
        "disaster_impact": 0.2,
        "catastrophe_threshold": 0.0,
        "predator_chance": 0.05,
        "predator_threshold": 100,
        "predator_impact_percentage": 0.05,
        "growth_rate": 0.9,
        "death_rate": 0.7,  # Species are oddly resilient
        "competition_intensity": 0.2,  # Competition is low-value
        "carrying_capacity": 2000,
        "prosperity_threshold": 100,
        "prosperity_boost": 1.8,  # Huge boost from disasters/scarcity
        "optimal_density": 1200,  # Crowded ecosystems do better
        "density_efficiency": 0.5,
        "adaptive_environment": True,
        "memory_window": 100,
        "memory_sensitivity": 0.6,  # very stable
    },
    "sentient_world": {
        "name": "Sentient World",
        "description": "Biosphere is no longer passive — existence becomes a negotiation with the planet itself.",
        "icon": "🧠",
        "resource_availability": 0.9,
        "resource_regeneration_rate": 0.6,
        "temperature": 23.0,
        "pollution": 0.15,
        "seasonal_variation": 0.4,
        "mutation_rate": 0.25,
        "mutation_strength": 0.08,
        "interaction_strength": 0.7,
        "radiation_background": 0.2,
        "event_chance": 0.1,
        "disaster_chance": 0.08,
        "disaster_impact": 0.4,
        "catastrophe_threshold": 500,
        "predator_chance": 0.15,
        "predator_threshold": 300,
        "predator_impact_percentage": 0.2,
        "growth_rate": 1.0,
        "death_rate": 1.0,
        "competition_intensity": 0.6,
        "carrying_capacity": 1200,
        "prosperity_threshold": 150,
        "prosperity_boost": 1.3,
        "optimal_density": 800,
        "density_efficiency": 0.3,
        "adaptive_environment": True,  # New parameter to enable environmental feedback
    },
}

# filepath: /home/jtk/Dev/TerminalLifeform/src/utils/world_loader.py
