"""
File: stats.py
Author: Jtk III
Date: 2024-06-10
Description: Statistics and logging for the simulation.
"""

import json
import os
from datetime import datetime
from pathlib import Path

from colored import Back, Fore, Style

from utils.logging_config import setup_logger

logger = setup_logger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # goes up from src/ to project root
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)  # ensure logs/ exists
TOTALS_FILE = LOGS_DIR / "sim_totals.json"

final_totals = {
    "world_name": "",
    "run_id": "",
    "epochs": 0,
    "total_entities": 0,
    "total_alive_at_conclusion": 0,
    "total_struggling": 0,
    "total_thriving": 0,
    "total_deaths": 0,
    "total_births": 0,
    "total_disasters": 0,
    "total_mutations": 0,
    "max_entities": 0,
}


def update_totals(
    epochs: int,
    max_entities: int,
    world_name: str,
    total: int,
    alive: int,
    struggling: int,
    thriving: int,
):
    """
    Update the final totals based on the current state of entities.
    """
    final_totals.update(
        {
            "run_id": datetime.now().isoformat(timespec="seconds"),
            "world_name": world_name,
            "epochs": epochs,
            "total_entities": total,
            "total_alive_at_conclusion": alive,
            "total_struggling": struggling,
            "total_thriving": thriving,
            "max_entities": max_entities,
        }
    )

    logger.info(
        "\n"
        f"🌍 --- Final Totals for World: {world_name} --- {epochs} Epochs ---\n"
        f"📊 --- Run ID: {final_totals['run_id']} ---\n"
        f"🧬 {Fore.green}Total Entities:{Style.reset} {total}, "
        f"📈 {Fore.green}Max Entities:{Style.reset} {max_entities}, \n"
        f"💀 {Fore.green}Total Deaths:{Style.reset} {final_totals['total_deaths']}, "
        f"👶 {Fore.green}Total Births:{Style.reset} {final_totals['total_births']}, "
        f"🔬 {Fore.green}Total Mutations:{Style.reset} {final_totals['total_mutations']}, \n\n"
        f"✅ {Fore.green}Alive at Conclusion:{Style.reset} {alive}, "
        f"🌿 {Fore.green}Thriving:{Style.reset} {thriving}, "
        f"🫤 {Fore.green}Struggling:{Style.reset} {struggling}"
    )

    append_totals_to_file()


def append_totals_to_file(filename: Path = TOTALS_FILE):
    """
    Append the final totals to a specified JSON file.
    Each entry is appended as a new object in a list.
    """
    try:
        data = []
        if filename.exists():
            try:
                data = json.loads(filename.read_text())
            except json.JSONDecodeError:
                data = []

        data.append(final_totals.copy())
        filename.write_text(json.dumps(data, indent=2))
        logger.info(f"✅ Final totals appended to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to append totals to {filename}: {e}")


def event_tracker(event_type: str, **kwargs):
    """
    Generic tracker for different types of events: death, birth, disaster, mutation.
    Logs the event and updates the corresponding total.
    Args:
        event_type (str): Type of the event ('death', 'birth', 'disaster', 'mutation').
        kwargs: Additional data relevant to the event.
    """
    if event_type == "death":
        entity = kwargs.get("entity")
        time = kwargs.get("time")
        if entity:
            logger.info(
                f"{Back.yellow}{entity.id} - {entity.name} died. (Age:{entity.age}) at {time} {Style.reset}"
            )
        final_totals["total_deaths"] += 1

    elif event_type == "birth":
        entity = kwargs.get("entity")
        new_entity = kwargs.get("new_entity")
        time = kwargs.get("time")
        if entity and new_entity and time is not None:
            logger.debug(
                f"{Back.red}Time {time}: Entity {entity.id} reproduced! New entity {new_entity.id} - {new_entity.name} born.{Style.reset}"
            )
        final_totals["total_births"] += 1

    elif event_type == "disaster":
        event = kwargs.get("event")
        time = kwargs.get("time")
        name = kwargs.get("name")
        logger.warning(
            f"{Fore.blue}Disaster Event: {event} occurred during the {time} epoch - {name} died {Style.reset} "
        )
        final_totals["total_disasters"] += 1

    elif event_type == "mutation":
        name = kwargs.get("name")
        original_value = kwargs.get("original_value")
        new_value = kwargs.get("new_value")
        logger.debug(
            f"{Fore.green}Mutation Event: {name} mutated! Original Value: {original_value} - New Value: {new_value}.{Style.reset}"
        )
        final_totals["total_mutations"] += 1

    else:
        logger.warning(f"Unknown event type: {event_type}")


def compare_last_runs(n=5, filename: Path = TOTALS_FILE):
    """
    Compare and display the last n simulation runs from the log file.
    Args:
        n (int): Number of recent runs to display.
        filename (str): Path to the JSON file containing simulation totals.
    Returns:
        list: The last n simulation run entries, or an empty list if none found.
    """
    if not os.path.exists(filename):
        print("No simulation history found.")
        return []
    os.system("cls" if os.name == "nt" else "clear")
    with open(filename) as f:
        data = json.load(f)

    print(f"\n📊 Last {min(n, len(data))} Simulation Runs:\n")
    for entry in data[-n:]:
        print(
            f"🌍 {entry['world_name']:<20} "
            f"✅ Alive End: {entry['total_alive_at_conclusion']:<10} "
            f"👶 Births: {entry['total_births']:<5} | "
            f"💀 Deaths: {entry['total_deaths']:<5} | "
            f"📈 Max: {entry['max_entities']} "
        )
    #  Jtk says: Let's also return an average of alive at conclusion
    avg_alive = sum(e["total_alive_at_conclusion"] for e in data[-n:]) / min(
        n, len(data)
    )
    print(
        f"\n📈 Average Alive at end over last {min(n, len(data))} runs: {avg_alive:.2f}\n"
    )
    #  Jtk says: which world was used most often
    world_counts = {}
    for e in data:
        world = e["world_name"]
        world_counts[world] = world_counts.get(world, 0) + 1
    most_common_world = max(world_counts, key=world_counts.get)  # type: ignore
    # Display most commonly used world in a table-like format with average alive at conclusion
    print("\n")
    print(f"{'World Name':<25} {'Runs':<5} {'Avg Alive End':<13}")
    print("-" * 45)
    filtered_worlds = [
        (world, num_runs) for world, num_runs in world_counts.items() if num_runs > 1
    ]
    if filtered_worlds:
        # Calculate average alive at conclusion for each world
        world_alive_averages = {}
        for world, _ in filtered_worlds:
            alive_values = [
                entry["total_alive_at_conclusion"]
                for entry in data
                if entry["world_name"] == world
            ]
            avg_alive_for_world = sum(alive_values) / len(alive_values)
            world_alive_averages[world] = avg_alive_for_world

        for world, num_runs in sorted(
            filtered_worlds, key=lambda x: x[1], reverse=True
        ):
            avg_alive = world_alive_averages[world]
            print(f"{world:<25} {num_runs:<5} {avg_alive:<13.2f}")
        print(
            f"\n🌍 Most common worlds: {most_common_world} ({world_counts[most_common_world]} runs)"
        )
    else:
        print("No worlds used more than once.")
    return data[-n:]


# filepath: /home/jtk/Dev/TerminalLifeform/src/stats.py
