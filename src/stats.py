import json
import os
from datetime import datetime

from colored import Back, Fore, Style

from logging_config import setup_logger

logger = setup_logger(__name__)

final_totals = {
    "total_entities": 0,
    "total_alive_at_conclusion": 0,
    "total_struggling": 0,
    "total_thriving": 0,
    "total_deaths": 0,
    "total_births": 0,
    "total_disasters": 0,
    "total_mutations": 0,
    "name": "",
    "epochs": 0,
    "max_entities": 0,
}


def update_totals(
    epochs: int,
    max_entities: int,
    name: str,
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
            "name": name,
            "total_entities": total,
            "total_alive_at_conclusion": alive,
            "total_struggling": struggling,
            "total_thriving": thriving,
            "epochs": epochs,
            "max_entities": max_entities,
        }
    )

    logger.info(
        "\n"
        f"--- Final Totals for World: {name} --- {epochs} Epochs ---\n"
        f"--- Run ID: {final_totals['run_id']} ---\n"
        f"{Fore.green}Total Entities:{Style.reset} {total}, "
        f"{Fore.green}Max Entities:{Style.reset} {max_entities}, "
        f"{Fore.green}Total Deaths:{Style.reset} {final_totals['total_deaths']}, "
        f"{Fore.green}Total Births:{Style.reset} {final_totals['total_births']}, "
        f"{Fore.green}Total Mutations:{Style.reset} {final_totals['total_mutations']}, "
        "\n --- Summary ---"
        f"{Fore.green}Alive at Conclusion:{Style.reset} {alive}, "
        f"{Fore.green}Thriving:{Style.reset} {thriving}, "
        f"{Fore.green}Struggling:{Style.reset} {struggling}"
    )

    append_totals_to_file()


def append_totals_to_file(filename: str = "logs/sim_totals.json"):
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
