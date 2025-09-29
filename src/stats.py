import json
import os
from datetime import datetime

from colored import Back, Fore, Style

from utils.logging_config import setup_logger

logger = setup_logger(__name__)
totals_json = "../logs/sim_totals.json"

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


def append_totals_to_file(filename: str = totals_json):
    """
    Append the final totals to a specified JSON file.
    Each entry is appended as a new object in a list.
    """
    try:
        data = []
        if os.path.exists(filename):
            with open(filename) as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
        data.append(final_totals.copy())
        with open(filename, "w") as file:
            json.dump(data, file, indent=2)
        logger.info(f"Final totals appended to {filename}")
    except Exception as e:
        logger.error(f"Failed to append totals to {filename}: {e}")


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


def compare_last_runs(n=5, filename=totals_json):
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

    with open(filename) as f:
        data = json.load(f)

    print(f"\n📊 Last {min(n, len(data))} Simulation Runs:\n")
    for entry in data[-n:]:
        print(
            f"🌍 {entry['world_name']:<20} | "
            f"📈 Max: {entry['max_entities']:<5} | "
            f"👶 Births: {entry['total_births']:<5} | "
            f"💀 Deaths: {entry['total_deaths']:<5} | "
            f"✅ Alive End: {entry['total_alive_at_conclusion']}"
        )
    return data[-n:]
