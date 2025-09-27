import sys

from sim import Simulation
from utils.world_loader import (
    add_mutant_worlds,
    load_world,
)  # , list_worlds, describe_world, evolve_world

if __name__ == "__main__":
    add_mutant_worlds()  # Ensure mutant worlds are added
    name = sys.argv[1] if len(sys.argv) > 1 else "garden_world"
    world_type = load_world(name)

    my_simulation = Simulation(
        initial_entities=120,
        time_steps=200,
        world=world_type,
    )
    my_simulation.run_simulation()

# To run: python src/main.py [world_preset_name]
# python main.py dunbars_world
# Available presets: default, harsh_world, garden_world, dunbars_world, chaotic_world,
