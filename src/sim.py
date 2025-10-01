"""
File: sim.py
Author: Jtk III
Date: 2024-06-10
Description: Core simulation engine for Terminal Lifeform.
"""

import math
import random
import time

from colored import Back, Fore, Style
from tqdm import tqdm

from entity import Entity
from enviroment import adapt_environment, apply_feedback_loops, update_environment
from events import (
    trigger_natural_disaster,
    trigger_predator_event,
    trigger_random_events,
)
from stats import event_tracker, update_totals
from utils.entity_utils import (
    calc_energy_change,
    calc_health_change,
    validate_entity_params,
)
from utils.logging_config import setup_logger
from utils.utils import pause_simulation, time_passes

logger = setup_logger(__name__)


class Simulation:
    """
    Manages the overall simulation, including entities, time, and environment.
    """

    def __init__(self, world, initial_entities=5, time_steps=1000):
        self.entities = []
        self.current_time = 0
        self.total_entities = 0
        self.epochs = time_steps
        self.max_entities = 0
        self.count = 0
        self.boom_count = 0
        self.drift = random.uniform(0.95, 1.05)
        self.last_boom_epoch = -20  # Ensure first boom can happen after 20 epochs
        self.population_history: list[int] = []
        self.memory_window: int = 17  # how many epochs back the world 'remembers'
        self.memory_window = world.get("memory_window", 50)
        self.memory_sensitivity = world.get("memory_sensitivity", 1.0)

        if isinstance(world, dict):
            self.environment_factors = world.copy()
            self.world_name = world.get("name", "default")
            self.world_description = world.get("description", "")
        else:
            raise ValueError("Simulation 'world' parameter must be a dict")

        for _ in range(initial_entities):
            self.add_entity(Entity())

        logger.info(f"Simulation initialized with {len(self.entities)} entities.")

    def add_entity(self, entity: Entity):
        validate_entity_params(entity.parameters)
        self.entities.append(entity)
        self.total_entities += 1
        logger.info(f"Added new entity: {entity.id}: {entity.name}")

    def natural_disaster(self, severity: float):
        # Dynamic Event: Natural Disaster if pollution or temp too high
        logger.info("\n 💨 Natural Disaster!")
        if (
            self.environment_factors["pollution"] > 0.5
            or self.environment_factors["temperature"] > 35.0
        ) and random.random() < self.environment_factors["disaster_chance"]:
            # Disaster occurs
            alive_count = len([e for e in self.entities if e.is_alive()])
            num_to_remove = int(
                alive_count * self.environment_factors["disaster_impact"] * severity
            )
            num_to_remove = max(1, num_to_remove)  # Ensure at least 1 entity is removed

            removed_entities = []

            for entity in random.sample(
                [e for e in self.entities if e.is_alive()],
                min(num_to_remove, alive_count),
            ):
                entity.health = 0  # Disaster instantly kills
                entity.update_status()  # Mark as dead
                removed_entities.append(entity.name)

            event_tracker(
                "disaster",
                event="Natural Disaster!",
                time=self.current_time,
                name=len(removed_entities),
            )

    def baby_boom(self):
        logger.info("\n👶 Baby Boom!")
        pause_simulation(20, desc="baby boom...", delay=0.05)
        # Dynamic Event: Baby Boom if population is low
        alive_count = len([e for e in self.entities if e.is_alive()])

        num_new_babies = int(alive_count * 0.3) + 3  # At least 3 new babies
        num_new_babies = min(num_new_babies, 150)  # Cap at 150 new babies

        new_entities = []
        thriving_alive_entities = [
            e for e in self.entities if e.is_alive() and e.status != "struggling"
        ]
        if thriving_alive_entities:
            for _ in range(num_new_babies):
                parent = random.choice(thriving_alive_entities)
                offspring_params = parent.parameters.copy()
                offspring_params["initial_health"] = random.uniform(80, 100)
                offspring_params["initial_energy"] = random.uniform(80, 100)
                new_entity = Entity(offspring_params)
                new_entities.append(new_entity)
                self.total_entities += 1
        else:
            logger.info("No thriving and alive entities available for baby boom event.")

        self.entities.extend(new_entities)
        self.environment_factors["growth_rate"] *= 1.18
        self.environment_factors["mutation_rate"] *= 1.12  # evolution speeds up
        self.environment_factors["interaction_strength"] *= (
            0.9  # less competition during expansion
        )
        self.environment_factors["resource_availability"] = min(
            1.0, self.environment_factors["resource_availability"] + 0.15
        )  # more resources during expansion

        self.environment_factors["temperature"] = max(
            6.0, self.environment_factors["temperature"] + 3.0
        )  # warmer during expansion
        self.environment_factors["pollution"] = max(
            0.0, self.environment_factors["pollution"] + 0.1
        )  # more pollution during expansion

        event_tracker(
            "birth",
            event="Baby Boom!",
            time=self.current_time,
            name=f"{num_new_babies} new entities born.",
        )

    def process_entity(self, entity):
        """
        Applies all updates to a single entity for the current Epoch.
        """

        if not entity.is_alive():
            return  # Skip dead entities

        for entity in self.entities:  # Update entity's environmental memory
            condition = self.environment_factors["resource_availability"] - 0.5
            # Positive if abundant, negative if scarce
            entity.environment_memory.append(condition)
            if len(entity.environment_memory) > entity.memory_span:
                entity.environment_memory.pop(0)

        entity.age += 1
        energy_change = calc_energy_change(entity, self.environment_factors)
        entity.energy = max(0.0, min(100.0, entity.energy + energy_change))
        health_change = calc_health_change(entity, self.environment_factors)
        entity.health = max(0.0, min(100.0, entity.health + health_change))
        entity.update_status()

    def adapt_entities(self):
        """
        Adjust entity traits based on environmental history.
        Resets memory on significant mutation to simulate evolutionary leaps.
        """
        for entity in self.entities:
            if not entity.is_alive():
                continue

            # Initialize memory-related attributes if missing
            if not hasattr(entity, "environment_memory"):
                entity.environment_memory = []
            if not hasattr(entity, "memory_span"):
                entity.memory_span = 20

            # Record current environment condition relative to baseline
            condition = self.environment_factors["resource_availability"] - 0.5
            entity.environment_memory.append(condition)
            if len(entity.environment_memory) > entity.memory_span:
                entity.environment_memory.pop(0)

            avg_condition = sum(entity.environment_memory) / len(
                entity.environment_memory
            )

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
            if (
                random.random()
                < self.environment_factors.get("mutation_rate", 0.05) * 0.1
            ):
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
            entity.reproduction_chance = max(
                0.001, min(entity.reproduction_chance, 2.0)
            )

    def efficiency_modifier(self, alive_count):
        if alive_count > self.environment_factors["prosperity_threshold"]:
            self.environment_factors["growth_rate"] *= self.environment_factors[
                "prosperity_boost"
            ]

        # Apply density-based efficiency modifier
        efficiency = 1 + self.environment_factors["density_efficiency"] * math.exp(
            -((alive_count - self.environment_factors["optimal_density"]) ** 2) / 50000
        )
        self.environment_factors["growth_rate"] *= efficiency

    def handle_interactions(self):
        """
        Handles interactions between entities, e.g., resource competition.
        """
        alive_entities = [e for e in self.entities if e.is_alive()]
        num_alive = len(alive_entities)

        if num_alive < 2:
            # No interactions if less than 2 entities
            logger.debug(
                f"{Style.BOLD}{Fore.cyan}No entities to interact with.{Style.reset}"
            )
            return

        # Interaction intensity increases with population density and low resources
        interaction_modifier = (
            1.0 - self.environment_factors["resource_availability"]
        ) + (num_alive / 100.0)  # Simple scaling
        interaction_modifier = min(
            1.0, max(0.1, interaction_modifier)
        )  # Clamp between 0.1 and 1.0

        for _, entity1 in enumerate(alive_entities):
            # Each entity interacts with a small random subset of others
            # To avoid N*N complexity for large populations
            num_interactions = min(
                num_alive - 1, 3
            )  # Interact with up to 3 other entities
            potential_targets = [e for e in alive_entities if e.id != entity1.id]

            if not potential_targets:
                continue

            for entity2 in random.sample(potential_targets, num_interactions):
                # Simple competition: entities lose health/energy based on aggression and resource scarcity
                if entity1.is_alive() and entity2.is_alive():
                    # Entity1 impacts Entity2
                    damage_to_entity2 = (
                        entity1.parameters["aggression"]
                        * self.environment_factors["interaction_strength"]
                        * interaction_modifier
                    )
                    entity2.health = max(0.0, entity2.health - damage_to_entity2 + 0.1)
                    entity2.energy = max(
                        0.0, entity2.energy - damage_to_entity2 / 2
                    )  # Energy loss is half of health loss

                    # Entity2 impacts Entity1 (can be symmetrical or asymmetrical)
                    damage_to_entity1 = (
                        entity2.parameters["aggression"]
                        * self.environment_factors["interaction_strength"]
                        * interaction_modifier
                    )
                    entity1.health = max(0.0, entity1.health - damage_to_entity1)
                    entity1.energy = max(
                        0.0, entity1.energy - damage_to_entity1 / 2 + 0.1
                    )

                    logger.debug(
                        f"Time {self.current_time}: Interaction between {entity1.id} and {entity2.id}. "
                        f"E1 Health:{entity1.health:.1f}, E2 Health:{entity2.health:.1f}"
                    )
                    # Note: Using debug level for frequent interaction logs to avoid overwhelming INFO level output

    def apply_mutation(self, params: dict) -> dict:
        """
        Applies slight random mutations to entity parameters.
        """
        mutated_params = params.copy()
        mutation_rate = self.environment_factors["mutation_rate"]
        mutation_strength = self.environment_factors["mutation_strength"]

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

    def over_population(self):
        logger.info(
            f"📢 {Back.magenta}Population pushing sustainable limits captain!{Style.reset}"
        )
        self.environment_factors["growth_rate"] *= 0.85
        self.environment_factors["mutation_rate"] *= 1.1  # evolution speeds up
        self.environment_factors["interaction_strength"] *= (
            1.1  # more competition when over capacity
        )
        self.environment_factors["resource_availability"] *= 0.8
        self.environment_factors["pollution"] = min(
            1.0, self.environment_factors["pollution"] + 0.1
        )
        self.environment_factors["temperature"] += 1.0

    def handle_reproduction(self):
        """
        Checks for thriving entities and potentially adds new offspring.
        """
        new_entities = []
        for entity in self.entities:
            if (
                entity.status != "struggling"
                and entity.age >= entity.parameters["min_reproduction_age"]
                and random.random() < entity.parameters["reproduction_chance"]
            ):
                offspring_params = entity.parameters.copy()
                offspring_params = self.apply_mutation(offspring_params)
                offspring_params["initial_health"] = random.uniform(80, 100)
                offspring_params["initial_energy"] = random.uniform(80, 100)

                new_entity = Entity(offspring_params)
                new_entities.append(new_entity)
                self.total_entities += 1
                entity.health -= 3.0  # Parent loses some health after reproduction

                event_tracker(
                    "birth",
                    entity=entity,
                    new_entity=new_entity,
                    time=self.current_time,
                )

        self.entities.extend(new_entities)

    def run_simulation(self):  # noqa: C901
        """
        Runs the simulation for the specified number of Epochs.
        """

        logger.info(
            f"\n🌍 Terminal Lifeform in {self.world_name} world; 📜 {self.world_description}"
        )
        pause_simulation(20, desc="init term lifeform...", delay=0.05)

        # Main simulation loop
        for t in tqdm(range(self.epochs), desc="Terminal Lifeform Sim Progress"):
            self.current_time = t
            self.count += 1
            logger.info(f"\n--- Epoch {self.current_time} ---")
            time.sleep(0.33)  # Simulate time passing

            if random.random() < self.environment_factors["event_chance"]:
                trigger_random_events(self)

            trigger_predator_event(self, severity=0.3)
            trigger_natural_disaster(self, severity=0.25)

            logger.info(
                f"{Fore.blue}Environment:{Style.reset} {Fore.green} \
                Resources:{self.environment_factors['resource_availability']:.2f},  "
                f"Temp:{self.environment_factors['temperature']:.1f}C, \
                 Pollution:{self.environment_factors['pollution']:.2f} {Style.reset}"
            )

            time_passes(0.75)  # Simulate time passing

            for entity in self.entities:
                self.process_entity(entity)  # Process each entity individually

            self.handle_interactions()  # interactions between entities

            if entity.environment_memory:
                avg_condition = sum(entity.environment_memory) / len(
                    entity.environment_memory
                )

                # If life’s been tough, evolve survival mode:
                if avg_condition < -0.1:
                    entity.resilience *= 1.05
                    entity.metabolism_rate *= 0.95
                    entity.reproduction_chance *= 0.9

                # If life’s been great, go growth mode:
                elif avg_condition > 0.1:
                    entity.resilience *= 0.95
                    entity.metabolism_rate *= 1.05
                    entity.reproduction_chance *= 1.1

                # Slight random drift to avoid stagnation
                entity.resilience *= self.drift
                entity.metabolism_rate *= self.drift

            self.handle_reproduction()

            self.adapt_entities()  # Phenotypic plasticity: short-term adaptation

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
                logger.info(
                    f"{Back.magenta}All entities have died. Simulation ending early.{Style.reset}"
                )
                break  # They're all dead, Jim.
            else:
                # We have survivors, let's process them
                self.efficiency_modifier(alive_count)

                if alive_count > self.max_entities:
                    self.max_entities = alive_count

                if alive_count > self.environment_factors["carrying_capacity"]:
                    self.over_population()

                if len(self.population_history) > self.memory_window:
                    self.population_history.pop(0)  # keep memory bounded

                if (
                    alive_count < self.environment_factors["optimal_density"]
                    and self.count > 16
                    and random.random() < 0.2
                ):
                    if self.boom_count < 7:  # Limit number of baby booms
                        # Only allow baby boom if last one was >10 loops ago
                        if (
                            not hasattr(self, "last_boom_epoch")
                            or (self.current_time - self.last_boom_epoch) > 10
                        ):
                            self.baby_boom()  # Check for baby boom events
                            self.boom_count += 1
                            self.last_boom_epoch = self.current_time
                        else:
                            logger.info("Baby boom skipped: last boom was too recent.")
                    else:
                        logger.info("Maximum number of baby booms reached.")

                update_environment(self)  # Update environment for next Epoch
                apply_feedback_loops(
                    self, alive_count
                )  # Dynamic environmental feedback
                adapt_environment(
                    self
                )  # If world supports it, adaptively change environment

                logger.info(
                    f" {Back.magenta}Alive={alive_count}, Thriving={thriving_count}, Struggling={struggling_count}{Style.reset}"
                )

        logger.info(
            f"\n--- Simulation {self.world_name} Finished at Epoch {self.current_time} ---"
        )

        update_totals(
            self.epochs,
            self.max_entities,
            self.world_name,
            self.total_entities,
            alive_count,
            struggling_count,
            thriving_count,
        )
