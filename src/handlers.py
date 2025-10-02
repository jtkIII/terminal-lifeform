import math
import random

from colored import Back, Fore, Style

from entity import Entity
from stats import event_tracker
from utils.logging_config import setup_logger
from utils.utils import pause_simulation

logger = setup_logger(__name__)


def handle_interactions(sim):
    """
    Handles interactions between entities, e.g., resource competition.
    """
    alive_entities = [e for e in sim.entities if e.is_alive()]
    num_alive = len(alive_entities)

    if num_alive < 2:
        # No interactions if less than 2 entities
        logger.debug(
            f"{Style.BOLD}{Fore.cyan}No entities to interact with.{Style.reset}"
        )
        return

    # Interaction intensity increases with population density and low resources
    interaction_modifier = (1.0 - sim.environment_factors["resource_availability"]) + (
        num_alive / 100.0
    )  # Simple scaling
    interaction_modifier = min(
        1.0, max(0.1, interaction_modifier)
    )  # Clamp between 0.1 and 1.0

    for _, entity1 in enumerate(alive_entities):
        # Each entity interacts with a small random subset of others
        # To avoid N*N complexity for large populations
        num_interactions = min(num_alive - 1, 3)  # Interact with up to 3 other entities
        potential_targets = [e for e in alive_entities if e.id != entity1.id]

        if not potential_targets:
            continue

        for entity2 in random.sample(potential_targets, num_interactions):
            # Simple competition: entities lose health/energy based on aggression and resource scarcity
            if entity1.is_alive() and entity2.is_alive():
                # Entity1 impacts Entity2
                damage_to_entity2 = (
                    entity1.parameters["aggression"]
                    * sim.environment_factors["interaction_strength"]
                    * interaction_modifier
                )
                entity2.health = max(0.0, entity2.health - damage_to_entity2 + 0.1)
                entity2.energy = max(
                    0.0, entity2.energy - damage_to_entity2 / 2
                )  # Energy loss is half of health loss

                # Entity2 impacts Entity1 (can be symmetrical or asymmetrical)
                damage_to_entity1 = (
                    entity2.parameters["aggression"]
                    * sim.environment_factors["interaction_strength"]
                    * interaction_modifier
                )
                entity1.health = max(0.0, entity1.health - damage_to_entity1)
                entity1.energy = max(0.0, entity1.energy - damage_to_entity1 / 2 + 0.1)

                logger.debug(
                    f"Time {sim.current_time}: Interaction between {entity1.id} and {entity2.id}. "
                    f"E1 Health:{entity1.health:.1f}, E2 Health:{entity2.health:.1f}"
                )
                # Note: Using debug level for frequent interaction logs to avoid overwhelming INFO level output


def handle_reproduction(sim):
    """
    Checks for thriving entities and potentially adds new offspring.
    """
    new_entities = []
    for entity in sim.entities:
        if (
            entity.status != "struggling"
            and entity.age >= entity.parameters["min_reproduction_age"]
            and random.random() < entity.parameters["reproduction_chance"]
        ):
            offspring_params = entity.parameters.copy()
            offspring_params = handle_mutation(sim, offspring_params)
            offspring_params["initial_health"] = random.uniform(80, 100)
            offspring_params["initial_energy"] = random.uniform(80, 100)

            new_entity = Entity(offspring_params)
            new_entities.append(new_entity)
            sim.total_entities += 1
            entity.health -= 3.0  # Parent loses some health after reproduction

            event_tracker(
                "birth",
                entity=entity,
                new_entity=new_entity,
                time=sim.current_time,
            )

    sim.entities.extend(new_entities)


def handle_efficiency_modifier(sim, population):
    if population > sim.environment_factors["prosperity_threshold"]:
        sim.environment_factors["growth_rate"] *= sim.environment_factors[
            "prosperity_boost"
        ]

    # Apply density-based efficiency modifier
    efficiency = 1 + sim.environment_factors["density_efficiency"] * math.exp(
        -((population - sim.environment_factors["optimal_density"]) ** 2) / 50000
    )

    sim.environment_factors["growth_rate"] *= efficiency


def handle_over_population(sim, population):
    if population < sim.environment_factors["carrying_capacity"]:
        return  # Population is within sustainable limits

    logger.info(
        f"📢 {Back.magenta}Population pushing sustainable limits captain!{Style.reset}"
    )
    sim.environment_factors["growth_rate"] *= 0.85
    sim.environment_factors["mutation_rate"] *= 1.1  # evolution speeds up
    sim.environment_factors["interaction_strength"] *= (
        1.1  # more competition when over capacity
    )
    sim.environment_factors["resource_availability"] *= 0.8
    sim.environment_factors["pollution"] = min(
        1.0, sim.environment_factors["pollution"] + 0.1
    )
    sim.environment_factors["temperature"] += 1.0


def handle_mutation(sim, params: dict) -> dict:
    """
    Applies slight random mutations to entity parameters.
    """
    mutated_params = params.copy()
    mutation_rate = sim.environment_factors["mutation_rate"]
    mutation_strength = sim.environment_factors["mutation_strength"]

    # Parameters that can mutate and their bounds/types
    mutable_parameters = {
        "max_age": {"min": 50, "max": 99, "type": int},
        "metabolism_rate": {"min": 0.2, "max": 0.9, "type": float},
        "resilience": {"min": 0.2, "max": 0.8, "type": float},
        "reproduction_chance": {"min": 0.01, "max": 0.15, "type": float},
        "aggression": {"min": 0.0, "max": 0.9, "type": float},
    }

    for param_name, config in mutable_parameters.items():
        if random.random() < mutation_rate:
            original_value = mutated_params[param_name]
            change = original_value * random.uniform(
                -mutation_strength, mutation_strength
            )

            if config["type"] is int:
                new_value = int(round(original_value + change))
            else:  # float
                new_value = original_value + change

            # Apply bounds
            new_value = max(config["min"], min(config["max"], new_value))
            mutated_params[param_name] = new_value
            event_tracker(
                "mutation",
                name=param_name,
                original_value=original_value,
                new_value=new_value,
            )

    return mutated_params


def handle_baby_boom(sim, alive_count):
    if random.random() > 0.2:  # 80% chance to trigger baby boom
        return

    if (
        alive_count > sim.environment_factors["optimal_density"]
        and sim.epoch_count < 16
        and sim.boom_count > 7
    ):
        return  # Too crowded or too early or too many booms already

    logger.info("\n👶 Baby Boom!")
    pause_simulation(20, desc="baby boom...", delay=0.05)

    alive_count = len([e for e in sim.entities if e.is_alive()])
    num_new_babies = int(alive_count * 0.3) + 3  # At least 3 new babies
    num_new_babies = min(num_new_babies, 150)  # Cap at 150 new babies

    new_entities = []
    thriving_alive_entities = [
        e for e in sim.entities if e.is_alive() and e.status != "struggling"
    ]
    if thriving_alive_entities:
        for _ in range(num_new_babies):
            parent = random.choice(thriving_alive_entities)
            offspring_params = parent.parameters.copy()
            offspring_params["initial_health"] = random.uniform(80, 100)
            offspring_params["initial_energy"] = random.uniform(80, 100)
            new_entity = Entity(offspring_params)
            new_entities.append(new_entity)
            sim.total_entities += 1
    else:
        logger.info("No thriving and alive entities available for baby boom event.")

    sim.entities.extend(new_entities)
    sim.environment_factors["growth_rate"] *= 1.18
    sim.environment_factors["mutation_rate"] *= 1.12  # evolution speeds up
    sim.environment_factors["interaction_strength"] *= (
        0.9  # less competition during expansion
    )
    sim.environment_factors["resource_availability"] = min(
        1.0, sim.environment_factors["resource_availability"] + 0.15
    )  # more resources during expansion

    sim.environment_factors["temperature"] = max(
        6.0, sim.environment_factors["temperature"] + 3.0
    )  # warmer during expansion
    sim.environment_factors["pollution"] = max(
        0.0, sim.environment_factors["pollution"] + 0.1
    )  # more pollution during expansion

    event_tracker(
        "birth",
        event="Baby Boom!",
        time=sim.current_time,
        name=f"{num_new_babies} new entities born.",
    )
