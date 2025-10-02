"""
File: entity.py
Author: Jtk III
Date: 2024-06-10
Description: Defines the Entity class representing individuals in the simulation.
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum

from faker import Faker

from params import entity_params

fake = Faker(["it_IT", "en_US", "en_GB", "en_NZ"])
WORLD_WIDTH = 1920
WORLD_HEIGHT = 1080


class Status(Enum):
    THRIVING = "thriving"
    STRUGGLING = "struggling"
    ALIVE = "alive"
    DORMANT = "dormant"
    EXPLORING = "exploring"
    DEAD = "dead"


@dataclass
class Entity:
    """
    Represents an individual entity in the simulation.

    Attributes:
        id (str): Unique identifier for the entity.
        age (int): Current age of the entity (in simulation Epochs).
        health (float): Current health of the entity (0.0 to 100.0).
        energy (float): Current energy level of the entity (0.0 to 100.0).
        status (str): Current status (e.g., 'alive', 'dead', 'thriving', 'struggling').
        parameters (dict): Customizable parameters for this specific entity type.
                           Examples: 'max_age', 'metabolism_rate', 'resilience'.
    """

    def __init__(self, initial_parameters: dict = None):  # type: ignore
        """
        Initializes a new entity with default or provided parameters.

        Args:
            initial_parameters A dictionary of custom parameters for this entity. Defaults2 to None.
        """
        self.id = str(uuid.uuid4())[:8]
        self.age = 0
        # self.status = "alive"
        self.parameters = entity_params.copy()
        self.status = Status.ALIVE.value

        # Spatial fields
        self.x: int = field(default_factory=lambda: random.randint(0, WORLD_WIDTH))
        self.y: int = field(default_factory=lambda: random.randint(0, WORLD_HEIGHT))

        self.environment_memory = []  # rolling record of past conditions
        self.memory_span = 20  # how far back they “remember”
        self.adaptation_bias = 1.0  # baseline multiplier for adaptation

        if random.uniform(1, 3) % 2 == 0:
            self.name = fake.first_name_nonbinary()
        else:
            self.name = fake.last_name_nonbinary()

        # Override default parameters with any provided initial_parameters
        if initial_parameters:
            self.parameters.update(initial_parameters)

        # "max_age": 99,

        # "health_recovery_rate": 1.15,
        # "health_decay_rate": 1.35,
        # "thriving_threshold_health": 65.0,
        # "thriving_threshold_energy": 60.0,
        # "struggling_threshold_health": 33.0,
        # "struggling_threshold_energy": 22.0,
        # "min_reproduction_age": 13,
        # "aggression": 0.3,
        # "cooperation": 0.1,

        self.health = self.parameters["initial_health"]
        self.energy = self.parameters["initial_energy"]
        self.resilience = self.parameters.get("resilience", 0.1)
        self.foraging_efficiency = self.parameters.get("foraging_efficiency", 0.1)
        self.metabolism_rate = self.parameters.get("metabolism_rate", 0.1)
        self.reproduction_chance = self.parameters.get("reproduction_chance", 0.05)
        self.mutation_rate = self.parameters.get("mutation_rate", 0.01)
        self.aggression = self.parameters.get("aggression", 0.1)

    def is_alive(self) -> bool:
        # return self.status != "dead"
        return self.status != Status.DEAD.value

    def update_status(self) -> None:
        """
        Updates the entity's status based on its current health and energy.
        """
        if self.health <= 0 or self.age >= self.parameters["max_age"]:
            self.status = Status.DEAD.value
            self.health = 0.0
            self.energy = 0.0
        elif (
            self.health >= self.parameters["thriving_threshold_health"]
            and self.energy >= self.parameters["thriving_threshold_energy"]
        ):
            self.status = Status.THRIVING.value
        elif (
            self.health <= self.parameters["struggling_threshold_health"]
            or self.energy <= self.parameters["struggling_threshold_energy"]
        ):
            self.status = Status.STRUGGLING.value
        else:
            self.status = Status.ALIVE.value

    def __repr__(self) -> str:
        return (
            f"Entity({self.id}: {self.name} Age:{self.age}, Health:{self.health:.1f}, "
            f"Energy:{self.energy:.1f}, Status:'{self.status}')"
        )


# filepath: /home/jtk/Dev/TerminalLifeform/src/entity.py
