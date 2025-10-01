"""
File: main.py
Author: Jtk III
Date: 2024-06-10
Description: Entry point for the Terminal Lifeform simulation.
"""

import os
import sys

from sim import Simulation
from utils.world_loader import (
    add_mutant_worlds,
    choose_world,
    load_world,
)


def run_simulation(world_name: str):
    world_type = load_world(world_name)
    print(f"\n🚀 Launching simulation with world: {world_name}\n")

    my_simulation = Simulation(
        initial_entities=120,
        time_steps=200,
        world=world_type,
    )
    my_simulation.run_simulation()


if __name__ == "__main__":
    add_mutant_worlds()  # Ensure mutant worlds are added

    while True:
        if len(sys.argv) > 1:  # If a world name was provided as an argument, use it.
            world_name = sys.argv[1]
        else:
            os.system("cls" if os.name == "nt" else "clear")
            world_name = choose_world()  # Otherwise, show the interactive selector.

        run_simulation(world_name)

        again = input("\n🔁 Run another simulation? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("\n👋 Goodbye — until next evolution!\n")
            break

        sys.argv = [sys.argv[0]]  # clear CLI arg if used previously

# filepath: /home/jtk/Dev/TerminalLifeform/src/main.py
