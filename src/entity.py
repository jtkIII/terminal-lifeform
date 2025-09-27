# filepath: /home/jtk/Dev/TerminalLifeform/src/entity.py
import random
import uuid

from faker import Faker

from params import entity_params

fake = Faker(["it_IT", "en_US", "en_GB", "en_NZ"])


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

    def __init__(self, initial_parameters: dict = None):
        """
        Initializes a new entity with default or provided parameters.

        Args:
            initial_parameters A dictionary of custom parameters for this entity. Defaults to None.
        """
        self.id = str(uuid.uuid4())[:8]
        self.age = 0
        self.status = "alive"
        self.parameters = entity_params.copy()

        if random.uniform(1, 3) % 2 == 0:
            self.name = fake.first_name_nonbinary()
        else:
            self.name = fake.last_name_nonbinary()

        # Override default parameters with any provided initial_parameters
        if initial_parameters:
            self.parameters.update(initial_parameters)

        self.health = self.parameters["initial_health"]
        self.energy = self.parameters["initial_energy"]

    def is_alive(self) -> bool:
        return self.status != "dead"

    def update_status(self) -> None:
        """
        Updates the entity's status based on its current health and energy.
        """
        if self.health <= 0 or self.age >= self.parameters["max_age"]:
            self.status = "dead"
            self.health = 0.0
            self.energy = 0.0
        elif (
            self.health >= self.parameters["thriving_threshold_health"]
            and self.energy >= self.parameters["thriving_threshold_energy"]
        ):
            self.status = "thriving"
        elif (
            self.health <= self.parameters["struggling_threshold_health"]
            or self.energy <= self.parameters["struggling_threshold_energy"]
        ):
            self.status = "struggling"
        else:
            self.status = "alive"

    def __repr__(self) -> str:
        return (
            f"Entity({self.id}: {self.name} Age:{self.age}, Health:{self.health:.1f}, "
            f"Energy:{self.energy:.1f}, Status:'{self.status}')"
        )
