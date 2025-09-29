import random

from colored import Back, Fore, Style

from utils.logging_config import setup_logger

logger = setup_logger(__name__)


def trigger_random_events(sim):  # noqa: C901
    """
    Handle a random environmental event during the simulation.
    `sim` is the Simulation instance, so you can access:
       sim.environment_factors, sim.entities, sim.current_time, etc.
    """
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
