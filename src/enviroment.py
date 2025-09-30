from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def adapt_environment(sim):
    """
    Adaptive environment with ecological memory.
    World reacts to population pressure AND trends over time.
    """
    if not sim.environment_factors.get("adaptive_environment"):
        return

    alive_count = len([e for e in sim.entities if e.is_alive()])
    capacity = sim.environment_factors.get("carrying_capacity", 1000)
    density_ratio = alive_count / capacity

    if sim.population_history:
        avg_past = sum(sim.population_history) / len(sim.population_history)
    else:
        avg_past = alive_count

    # trend = (alive_count - avg_past) / avg_past if avg_past > 0 else 0.0
    trend = ((alive_count - avg_past) / avg_past) * sim.memory_sensitivity

    # --- Push back on persistent overgrowth ---
    if density_ratio > 1.2 or trend > 0.15:
        sim.environment_factors["resource_availability"] *= 0.9
        sim.environment_factors["disaster_chance"] *= 1.2
        sim.environment_factors["radiation_background"] *= 1.05
        sim.environment_factors["mutation_rate"] *= 1.1

        logger.info(
            f"🌍 Gaea remembers past abundance. Pop rising ({trend:+.2%}), "
            "resources restricted and disasters intensify."
        )

    # --- Assist recovery if population trending downward ---
    elif density_ratio < 0.4 or trend < -0.15:
        sim.environment_factors["resource_availability"] *= 1.12
        sim.environment_factors["disaster_chance"] *= 0.85
        sim.environment_factors["mutation_rate"] *= 1.15

        logger.info(
            f"🌱 Gaea recalls past collapse. Pop falling ({trend:+.2%}), "
            "resources increased to stabilize life."
        )

    # --- Optional: dampen overshooting ---
    if abs(trend) > 0.25:
        sim.environment_factors["mutation_rate"] *= 1.2
        logger.info("⚠️ Rapid change triggers evolutionary pressure!")

    # Clamp factors to avoid runaway values
    sim.environment_factors["resource_availability"] = max(
        0.1, min(sim.environment_factors["resource_availability"], 2.0)
    )
    sim.environment_factors["mutation_rate"] = max(
        0.01, min(sim.environment_factors["mutation_rate"], 0.8)
    )


def update_environment(sim):
    """
    Updates environmental factors over time or based on random events.
    """
    sim.environment_factors["resource_availability"] = max(
        0.1, 1.0 - (sim.current_time / sim.epochs) * 0.5
    )  # Gradual changes over time

    sim.environment_factors["temperature"] = 25.0 + 10 * (
        sim.current_time / sim.epochs - 0.5
    )  # Oscillates

    sim.environment_factors["pollution"] = min(
        0.8, (sim.current_time / sim.epochs) * 0.3
    )  # Gradual increase in polution over time

    sim.environment_factors["event_chance"] = min(
        0.1, sim.environment_factors["event_chance"] + 0.001
    )  # Slight increase in event chance over time

    sim.environment_factors["interaction_strength"] = min(
        1.0, sim.environment_factors["interaction_strength"] + 0.001
    )  # Should this decrease over time? Maybe not.

    sim.environment_factors["mutation_rate"] = min(
        0.3, sim.environment_factors["mutation_rate"] + 0.0005
    )  # Slight increase in mutation rate over time


def apply_feedback_loops(sim, population: int) -> None:
    """
    Mutate the world state in-place based on current population and environmental feedback loops.
    This creates emergent behavior where the simulation environment evolves dynamically over time.
    """

    # --- Resource feedback ---
    # As population grows, resources become scarcer unless regeneration is very high.
    pressure = population / (sim.environment_factors["carrying_capacity"] + 1)
    sim.environment_factors["resource_availability"] *= 1 - 0.1 * pressure
    sim.environment_factors["resource_availability"] = max(
        sim.environment_factors["resource_availability"], 0.05
    )

    # --- Pollution feedback ---
    # More population = more waste and pollution. But if population crashes, environment heals.
    pollution_change = 0.05 * pressure - 0.02 * (1 - pressure)
    sim.environment_factors["pollution"] = max(
        0.0, min(sim.environment_factors["pollution"] + pollution_change, 1.0)
    )

    # --- Mutation pressure feedback ---
    # Higher radiation or pollution boosts mutation rate slightly over time.
    sim.environment_factors["mutation_rate"] *= (
        1 + 0.1 * sim.environment_factors["radiation_background"]
    )
    sim.environment_factors["mutation_rate"] = min(
        sim.environment_factors["mutation_rate"], 1.0
    )

    # --- Carrying capacity evolution ---
    # If the population consistently approaches carrying capacity, the environment may adapt
    # (e.g., niche expansion or ecosystem collapse if overshoot persists).
    if pressure > 0.8:
        # Stressful overshoot: risk ecosystem degradation
        sim.environment_factors["carrying_capacity"] *= 0.995
    elif 0.3 < pressure < 0.6:
        # Sustainable level: slight growth over time
        sim.environment_factors["carrying_capacity"] *= 1.002

    # Keep carrying capacity reasonable
    sim.environment_factors["carrying_capacity"] = max(
        50, min(sim.environment_factors["carrying_capacity"], 10000)
    )

    # --- Disaster & event feedback ---
    # Pollution and radiation slightly increase disaster frequency and impact.
    sim.environment_factors["disaster_chance"] += (
        0.01 * sim.environment_factors["pollution"]
    )
    sim.environment_factors["disaster_impact"] += (
        0.01 * sim.environment_factors["radiation_background"]
    )

    # Keep them capped
    sim.environment_factors["disaster_chance"] = min(
        sim.environment_factors["disaster_chance"], 1.0
    )
    sim.environment_factors["disaster_impact"] = min(
        sim.environment_factors["disaster_impact"], 1.0
    )
