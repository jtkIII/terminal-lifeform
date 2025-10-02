"""
File: sim.py
Author: Jtk III
Date: 2024-06-10
Description: Core simulation engine for Terminal Lifeform.
"""

import random
import time

from colored import Back, Fore, Style
from tqdm import tqdm

from entity import Entity
from enviroment import (
    adapt_environment,
    apply_feedback_loops,
    handle_enviroment_memory,
    update_environment,
)
from events import (
    trigger_natural_disaster,
    trigger_predator_event,
    trigger_random_events,
)
from handlers import (
    handle_baby_boom,
    handle_efficiency_modifier,
    handle_interactions,
    handle_mutation,
    handle_over_population,
    handle_reproduction,
)
from stats import (
    event_tracker,
    record_trait_snapshot,
    save_trait_history,
    update_global_trait_tracker,
    update_totals,
)
from utils.entity_utils import adapt_entities, add_entity, process_entity
from utils.logging_config import setup_logger
from utils.utils import pause_simulation, time_passes

logger = setup_logger(__name__)


class Simulation:
    """
    Manages the overall simulation, including entities, time, and environment.
    """

    def __init__(self, world, init_ents=5, epochs=1000):
        self.entities = []
        self.current_time = 0
        self.total_entities = 0
        self.epochs = epochs
        self.max_entities = 0
        self.epoch_count = 0
        self.boom_count = 0
        self.drift = random.uniform(0.95, 1.05)
        self.last_boom_epoch = -20  # Ensure first boom can happen after 20 epochs
        self.population_history: list[int] = []
        self.memory_window: int = 17  # how many epochs back the world 'remembers'
        self.memory_window = world.get("memory_window", 50)
        self.memory_sensitivity = world.get("memory_sensitivity", 1.1)

        if isinstance(world, dict):
            self.environment_factors = world.copy()
            self.world_name = world.get("name", "default")
            self.world_description = world.get("description", "")
        else:
            raise ValueError("Simulation 'world' parameter must be a dict")

        for _ in range(init_ents):
            add_entity(self, Entity())

        logger.info(f"Simulation initialized with {len(self.entities)} entities.")

    def run_simulation(self):
        """
        Runs the simulation for the specified number of Epochs.
        """

        logger.info(f"\n🌍 Terminal Lifeform running {self.world_name} world")
        pause_simulation(20, desc="init term lifeform...", delay=0.05)

        # Main simulation loop
        for t in tqdm(range(self.epochs), desc="Terminal Lifeform Progress"):
            self.current_time = t
            self.epoch_count += 1
            logger.info(f"\n--- Epoch {self.current_time} ---")
            time.sleep(0.33)  # Simulate time passing

            trigger_random_events(self)
            trigger_predator_event(self, severity=0.3)
            trigger_natural_disaster(self, severity=0.25)

            logger.info(
                f"{Fore.blue}Resources:{self.environment_factors['resource_availability']:.2f},  "
                f"Temp:{self.environment_factors['temperature']:.1f}C, \
                 Pollution:{self.environment_factors['pollution']:.2f} {Style.reset}"
            )

            time_passes(0.75)  # Simulate time passing

            # First pass: process each entity
            for entity in self.entities:
                process_entity(self, entity)  # Process each entity individually
                if entity.environment_memory:
                    handle_enviroment_memory(entity, self.drift)

            handle_mutation(self, entity.parameters)
            handle_interactions(self)  # interactions between entities
            handle_reproduction(self)
            adapt_entities(self)  # Phenotypic plasticity: short-term adaptation

            # Second pass: update status and clean up dead entities
            for entity in self.entities:
                entity.update_status()  # Re-update status after interactions
                if entity.is_alive():
                    logger.info(f"{entity}")
                else:
                    event_tracker(
                        "death",
                        entity=entity,
                        time=self.current_time,
                    )

            self.entities = [entity for entity in self.entities if entity.is_alive()]

            alive_count = len(self.entities)
            self.population_history.append(alive_count)

            thriving_count = sum(1 for e in self.entities if e.status == "thriving")
            struggling_count = sum(1 for e in self.entities if e.status == "struggling")

            if alive_count == 0:
                logger.info(f"{Back.magenta}They're All Dead Jim{Style.reset}")
                break
            else:
                handle_efficiency_modifier(self, alive_count)
                handle_over_population(self, alive_count)

                if alive_count > self.max_entities:
                    self.max_entities = alive_count

                if len(self.population_history) > self.memory_window:
                    self.population_history.pop(0)  # keep memory bounded

                # Only allow baby boom if last one was >10 loops ago
                if (
                    not hasattr(self, "last_boom_epoch")
                    or (self.current_time - self.last_boom_epoch) > 10
                ):
                    handle_baby_boom(self, alive_count)
                    self.boom_count += 1
                    self.last_boom_epoch = self.current_time
                else:
                    logger.info("Baby boom skipped: last boom was too recent.")

                record_trait_snapshot(self.entities, self.epoch_count)
                update_environment(self)
                apply_feedback_loops(self, alive_count)
                adapt_environment(self)

                logger.info(
                    f" {Back.magenta}Alive={alive_count}, Thriving={thriving_count}, Struggling={struggling_count}{Style.reset}"
                )

        logger.info(
            f"\n--- Simulation {self.world_name} Finished at Epoch {self.current_time} ---"
        )

        save_trait_history()
        update_global_trait_tracker()

        update_totals(
            self.epochs,
            self.max_entities,
            self.world_name,
            self.total_entities,
            alive_count,
            struggling_count,
            thriving_count,
        )
