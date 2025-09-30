import os
import random
import sys

from sim import Simulation
from utils.world_loader import (
    WORLD_PRESETS,
    add_mutant_worlds,
    list_worlds,
    load_world,
)


def choose_world() -> str:
    """Prompt the user to choose a world preset interactively with descriptions and a random option."""
    worlds = list_worlds()

    print("\n🌍 Available Worlds:\n")
    for idx, name in enumerate(worlds, start=1):
        preset = WORLD_PRESETS[name]
        icon = preset.get("icon", "")
        desc = preset.get("description", "No description provided.")
        print(f"{idx:<2} {icon:<5} {name:<5} — {desc}")

    print("\n0. 🎲 Random World         — Choose a random preset from the list above")

    while True:
        choice = input("\nEnter the number of the world you want to run: ").strip()
        if choice.isdigit():
            choice_int = int(choice)
            if choice_int == 0:
                return random.choice(worlds)
            if 1 <= choice_int <= len(worlds):
                return worlds[choice_int - 1]
        print("❌ Invalid choice. Please enter a valid number.")


def run_simulation(world_name: str):
    """Load and run a simulation for the given world."""
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
