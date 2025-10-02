"""
File: events.py
Author: Jtk III
Date: 2024-06-10
Description: Random and dynamic event functions for the simulation.
"""

import random

from colored import Back, Style

from stats import event_tracker
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def trigger_random_events(sim):  # noqa: C901
    """
    Handle a random environmental event during the simulation.
    `sim` is the Simulation instance, so you can access:
       sim.environment_factors, sim.entities, sim.current_time, etc.
    """

    if random.random() > sim.environment_factors["event_chance"]:
        return  # No event this epoch

    logger.info("\n 🃏 Wild Card!")
    event_type = random.choice(
        [
            "resource_spike",
            "resource_crash",
            "disease_outbreak",
            "heatwave",
            "radiation_burst",
            "cold_snap",
            "meteor_strike",
            "mutagenic_wave",
        ]
    )

    if event_type == "resource_spike":
        sim.environment_factors["resource_availability"] = min(
            1.0, sim.environment_factors["resource_availability"] + 0.2
        )
        logger.info(
            f"Time {sim.current_time}: {Back.green}Environmental Event - Resource Spike!{Style.reset}"
        )

    elif event_type == "resource_crash":
        sim.environment_factors["resource_availability"] = max(
            0.0, sim.environment_factors["resource_availability"] - 0.3
        )
        sim.environment_factors["temperature"] = max(
            0.0, sim.environment_factors["temperature"] - random.uniform(5, 15)
        )
        logger.info(
            f"Time {sim.current_time}: {Back.red}Environmental Event - Resource Crash!{Style.reset}"
        )

    elif event_type == "disease_outbreak":
        for entity in random.sample(sim.entities, min(len(sim.entities), 10)):
            if entity.is_alive():
                entity.health = max(0, entity.health - random.uniform(10, 30))
        logger.info(
            f"Time {sim.current_time}: {Back.magenta}Environmental Event - Disease Outbreak!{Style.reset}"
        )

    elif event_type == "heatwave":
        sim.environment_factors["temperature"] = min(
            45.0, sim.environment_factors["temperature"] + random.uniform(5, 10)
        )
        logger.info(
            f"Time {sim.current_time}: {Back.yellow}Environmental Event - Heatwave!{Style.reset}"
        )

    elif event_type == "radiation_burst":
        for entity in random.sample(sim.entities, min(len(sim.entities), 5)):
            if entity.is_alive():
                entity.health = max(0, entity.health - random.uniform(20, 40))
        logger.info(
            f"Time {sim.current_time}: {Back.cyan}Environmental Event - Radiation Burst!{Style.reset}"
        )

    elif event_type == "cold_snap":
        sim.environment_factors["temperature"] = max(
            -10.0, sim.environment_factors["temperature"] - random.uniform(5, 15)
        )
        logger.info(
            f"Time {sim.current_time}: {Back.blue}Environmental Event - Cold Snap!{Style.reset}"
        )

    elif event_type == "meteor_strike":
        # Randomly kill a few entities outright
        victims = random.sample(sim.entities, min(len(sim.entities), 3))
        for entity in victims:
            entity.health = 0
        logger.info(
            f"Time {sim.current_time}: {Back.red}Environmental Event - Meteor Strike! {len(victims)} entities obliterated!{Style.reset}"
        )

    elif event_type == "mutagenic_wave":
        # Mutate some entities randomly
        for entity in random.sample(sim.entities, min(len(sim.entities), 5)):
            if entity.is_alive():
                entity.resilience *= random.uniform(1.1, 1.5)
                entity.foraging_efficiency *= random.uniform(0.9, 1.3)
        logger.info(
            f"Time {sim.current_time}: {Back.magenta}Environmental Event - Mutagenic Wave! Some entities evolved rapidly.{Style.reset}"
        )


def trigger_predator_event(sim, severity: float):
    # Dynamic Event: Predator if population is too high
    logger.info("\n💥 Disaster!")
    alive_count = len([e for e in sim.entities if e.is_alive()])

    predator_types = [
        ("Nucluear War", 0.8),
        ("Dimensional Rift", 0.75),
        ("Asteroid Impact", 0.7),
        ("Environmental Collapse", 0.65),
        ("Supervolcano", 0.6),
        ("Genetic Experiment Gone Wrong", 0.6),
        ("Ancient Beast", 0.55),
        ("Supernatural Entities", 0.5),
        ("Cybernetic Organisms", 0.5),
        ("Mutant Swarm", 0.45),
        ("Alien Invasion", 0.4),
        ("Sentient AI", 0.4),
        ("Robot Uprising", 0.35),
        ("Godzilla", 0.33),
        ("Apex Predator", 0.31),
        ("Space Pirates", 0.3),
        ("Time Travelers", 0.25),
        ("Human Sacrifice", 0.225),
        ("Zombie Outbreak", 0.2),
        ("Plague", 0.15),
        ("Mutant Wolf Pack", 0.1),
    ]
    predator_type, damage = random.choice(predator_types)

    if (
        alive_count > sim.environment_factors["predator_threshold"]
        and random.random() > sim.environment_factors["predator_chance"]
    ):
        num_to_remove = int(
            alive_count
            * sim.environment_factors["predator_impact_percentage"]
            * damage
            * severity
        )

        num_to_remove = max(1, num_to_remove)  # Ensure 1 entity is removed

        # Prioritize struggling entities if possible, otherwise random
        struggling_entities = [
            e for e in sim.entities if e.status == "struggling" and e.is_alive()
        ]
        if len(struggling_entities) >= num_to_remove:
            targets = random.sample(struggling_entities, num_to_remove)
        else:
            targets = random.sample(
                [e for e in sim.entities if e.is_alive()],
                min(num_to_remove, alive_count),
            )

        removed_entities = []

        for entity in targets:
            entity.health = 0  # Predator instantly kills
            entity.update_status()  # Mark as dead
            removed_entities.append(entity.name)

        event_tracker(
            "disaster",
            event=f"Disaster Alert! - {predator_type} Attack!!!",
            time=sim.current_time,
            name=len(removed_entities),
        )


def trigger_natural_disaster(sim, severity: float):
    # Dynamic Event: Natural Disaster if pollution or temp too high
    logger.info("\n 💨 Natural Disaster!")
    if (
        sim.environment_factors["pollution"] > 0.5
        or sim.environment_factors["temperature"] > 35.0
    ) and random.random() < sim.environment_factors["disaster_chance"]:
        # Disaster occurs
        alive_count = len([e for e in sim.entities if e.is_alive()])
        num_to_remove = int(
            alive_count * sim.environment_factors["disaster_impact"] * severity
        )
        num_to_remove = max(1, num_to_remove)  # Ensure at least 1 entity is removed

        removed_entities = []

        for entity in random.sample(
            [e for e in sim.entities if e.is_alive()],
            min(num_to_remove, alive_count),
        ):
            entity.health = 0  # Disaster instantly kills
            entity.update_status()  # Mark as dead
            removed_entities.append(entity.name)

        event_tracker(
            "disaster",
            event="Natural Disaster!",
            time=sim.current_time,
            name=len(removed_entities),
        )


# filepath: /home/jtk/Dev/TerminalLifeform/src/events.py
