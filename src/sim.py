import math
import random
import time

from colored import Back, Fore, Style
from tqdm import tqdm

from entity import Entity
from entity_utils import calc_energy_change, calc_health_change, validate_entity_params
from logging_config import setup_logger
from stats import event_tracker, update_totals
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

    def update_environment(self):
        """
        Updates environmental factors over time or based on random events.
        """
        self.environment_factors["resource_availability"] = max(
            0.1, 1.0 - (self.current_time / self.epochs) * 0.5
        )  # Gradual changes over time

        self.environment_factors["temperature"] = 25.0 + 10 * (
            self.current_time / self.epochs - 0.5
        )  # Oscillates

        self.environment_factors["pollution"] = min(
            0.8, (self.current_time / self.epochs) * 0.3
        )  # Gradual increase in polution over time

        self.environment_factors["event_chance"] = min(
            0.1, self.environment_factors["event_chance"] + 0.001
        )  # Slight increase in event chance over time

        self.environment_factors["interaction_strength"] = min(
            1.0, self.environment_factors["interaction_strength"] + 0.001
        )  # Should this decrease over time? Maybe not.

        self.environment_factors["mutation_rate"] = min(
            0.3, self.environment_factors["mutation_rate"] + 0.0005
        )  # Slight increase in mutation rate over time

    def natural_disaster(self, severity: float):
        # Dynamic Event: Natural Disaster if pollution or temp too high
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

    def predator_event(self, severity: float):
        # Dynamic Event: Predator if population is too high
        alive_count = len([e for e in self.entities if e.is_alive()])

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
            alive_count > self.environment_factors["predator_threshold"]
            and random.random() > self.environment_factors["predator_chance"]
        ):
            num_to_remove = int(
                alive_count
                * self.environment_factors["predator_impact_percentage"]
                * damage
                * severity
            )

            num_to_remove = max(1, num_to_remove)  # Ensure 1 entity is removed

            # Prioritize struggling entities if possible, otherwise random
            struggling_entities = [
                e for e in self.entities if e.status == "struggling" and e.is_alive()
            ]
            if len(struggling_entities) >= num_to_remove:
                targets = random.sample(struggling_entities, num_to_remove)
            else:
                targets = random.sample(
                    [e for e in self.entities if e.is_alive()],
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

    def random_events(self):
        event_type = random.choice(
            [
                "resource_spike",
                "resource_crash",
                "disease_outbreak",
                "heatwave",
                "radiation_burst",
            ]
        )

        if event_type == "resource_spike":
            self.environment_factors["resource_availability"] = min(
                1.0, self.environment_factors["resource_availability"] + 0.2
            )
            logger.info(
                f"Time {self.current_time}: {Back.red}Environmental Event - \
                    Resource Spike! {Style.reset}"
            )
        elif event_type == "resource_crash":
            self.environment_factors["resource_availability"] = max(
                0.0, self.environment_factors["resource_availability"] - 0.3
            )
            self.environment_factors["temperature"] = max(
                0.0, self.environment_factors["temperature"] - random.uniform(5, 15)
            )
            logger.info(
                f"Time {self.current_time}: {Back.red} Environmental Event \
                    - Resource Crash! {Style.reset}"
            )
        elif event_type == "disease_outbreak":
            # Reduce health of a random subset of entities
            for entity in random.sample(self.entities, min(len(self.entities), 10)):
                if entity.is_alive():
                    entity.health = max(0, entity.health - random.uniform(10, 30))
            logger.info(
                f"Time {self.current_time}: {Back.red} Environmental Event \
                    - Disease Outbreak! {Style.reset}"
            )
        elif event_type == "heatwave":
            self.environment_factors["temperature"] = min(
                45.0,
                self.environment_factors["temperature"] + random.uniform(5, 10),
            )
            logger.info(
                f"Time {self.current_time}: {Back.red} Environmental Event \
                    - Heatwave! {Style.reset}"
            )
        elif event_type == "radiation_burst":
            for entity in random.sample(self.entities, min(len(self.entities), 5)):
                if entity.is_alive():
                    entity.health = max(0, entity.health - random.uniform(20, 40))
            logger.info(
                f"Time {self.current_time}: {Back.red} Environmental Event \
                    - Radiation Burst! {Style.reset}"
            )

    def process_entity(self, entity):
        """
        Applies all updates to a single entity for the current Epoch.
        """

        if not entity.is_alive():
            return  # Skip dead entities

        entity.age += 1
        energy_change = calc_energy_change(entity, self.environment_factors)
        entity.energy = max(0.0, min(100.0, entity.energy + energy_change))
        health_change = calc_health_change(entity, self.environment_factors)
        entity.health = max(0.0, min(100.0, entity.health + health_change))
        entity.update_status()

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
            f"{Back.magenta}Population pushing sustainable limits captain!{Style.reset}"
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

    def apply_feedback_loops(self, population: int) -> None:
        """
        Mutate the world state in-place based on current population and environmental feedback loops.
        This creates emergent behavior where the simulation environment evolves dynamically over time.
        """

        # --- Resource feedback ---
        # As population grows, resources become scarcer unless regeneration is very high.
        pressure = population / (self.environment_factors["carrying_capacity"] + 1)
        self.environment_factors["resource_availability"] *= 1 - 0.1 * pressure
        self.environment_factors["resource_availability"] = max(
            self.environment_factors["resource_availability"], 0.05
        )

        # --- Pollution feedback ---
        # More population = more waste and pollution. But if population crashes, environment heals.
        pollution_change = 0.05 * pressure - 0.02 * (1 - pressure)
        self.environment_factors["pollution"] = max(
            0.0, min(self.environment_factors["pollution"] + pollution_change, 1.0)
        )

        # --- Mutation pressure feedback ---
        # Higher radiation or pollution boosts mutation rate slightly over time.
        self.environment_factors["mutation_rate"] *= (
            1 + 0.1 * self.environment_factors["radiation_background"]
        )
        self.environment_factors["mutation_rate"] = min(
            self.environment_factors["mutation_rate"], 1.0
        )

        # --- Carrying capacity evolution ---
        # If the population consistently approaches carrying capacity, the environment may adapt
        # (e.g., niche expansion or ecosystem collapse if overshoot persists).
        if pressure > 0.8:
            # Stressful overshoot: risk ecosystem degradation
            self.environment_factors["carrying_capacity"] *= 0.995
        elif 0.3 < pressure < 0.6:
            # Sustainable level: slight growth over time
            self.environment_factors["carrying_capacity"] *= 1.002

        # Keep carrying capacity reasonable
        self.environment_factors["carrying_capacity"] = max(
            50, min(self.environment_factors["carrying_capacity"], 10000)
        )

        # --- Disaster & event feedback ---
        # Pollution and radiation slightly increase disaster frequency and impact.
        self.environment_factors["disaster_chance"] += (
            0.01 * self.environment_factors["pollution"]
        )
        self.environment_factors["disaster_impact"] += (
            0.01 * self.environment_factors["radiation_background"]
        )

        # Keep them capped
        self.environment_factors["disaster_chance"] = min(
            self.environment_factors["disaster_chance"], 1.0
        )
        self.environment_factors["disaster_impact"] = min(
            self.environment_factors["disaster_impact"], 1.0
        )

    def run_simulation(self):
        """
        Runs the simulation for the specified number of Epochs.
        """

        logger.info(
            f"\n🌍 Terminal Lifeform Sim Init with the {self.world_name} world; 📜 {self.world_description}"
        )
        pause_simulation(20, desc="init term lifeform...", delay=0.05)

        # Main simulation loop
        for t in tqdm(range(self.epochs), desc="Terminal Lifeform Sim Progress"):
            self.current_time = t
            self.count += 1
            logger.info(f"\n--- Epoch {self.current_time} ---")
            time.sleep(0.33)  # Simulate time passing

            if random.random() < self.environment_factors["event_chance"]:
                self.random_events()  # Check for random events

            self.predator_event(severity=0.3)  # Check for predator events
            self.natural_disaster(severity=0.25)  # Check for natural disasters

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
            self.handle_reproduction()
            alive_count = len(self.entities)
            thriving_count = sum(1 for e in self.entities if e.status == "thriving")
            struggling_count = sum(1 for e in self.entities if e.status == "struggling")

            if alive_count == 0:
                logger.info(
                    f"{Back.magenta}All entities have died. Simulation ending early.{Style.reset}"
                )
                break  # They're all dead, Jim.
            else:
                # fight the bell curve collapse Apply prosperity-based growth modifier
                self.efficiency_modifier(alive_count)

                if alive_count > self.max_entities:
                    self.max_entities = alive_count

                if alive_count > self.environment_factors["carrying_capacity"]:
                    self.over_population()

                if (
                    alive_count < self.environment_factors["optimal_density"]
                    and self.count > 16
                    and random.random() < 0.25
                ):
                    self.baby_boom()  # Check for baby boom events

                self.update_environment()  # Update environment for next Epoch
                self.apply_feedback_loops(alive_count)  # Dynamic environmental feedback

                logger.info(
                    f" {Back.magenta} Population: Alive={alive_count}, Thriving={thriving_count}, Struggling={struggling_count}{Style.reset}"
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
