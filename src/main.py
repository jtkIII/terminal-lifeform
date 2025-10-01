"""
File: main.py
Author: Jtk III
Date: 2024-06-10
Description: Entry point for the Terminal Lifeform simulation.
"""

import os
import sys

from sim import Simulation
from utils.world_loader import choose_world, load_world


def run_simulation(world_name: str):
    world = load_world(world_name)
    my_simulation = Simulation(init_ents=120, epochs=150, world=world)
    my_simulation.run_simulation()


if __name__ == "__main__":
    while True:
        if len(sys.argv) > 1:  # If a world name was provided, use it
            world_name = sys.argv[1]
        else:
            os.system("cls" if os.name == "nt" else "clear")
            world_name = choose_world()  # Otherwise, show the menu

        run_simulation(world_name)

        again = input("\n❔ Run another simulation? (y/n): ").strip().lower()
        if again not in ("y", "yes"):  # Play again?
            print("\n 🖤 Allright then — until next evolution!\n")
            break

        sys.argv = [sys.argv[0]]  # clear CLI arg if used previously

# filepath: /home/jtk/Dev/TerminalLifeform/src/main.py
