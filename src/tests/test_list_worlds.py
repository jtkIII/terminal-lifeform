"""
File: test_list_worlds.py
Author: Jtk III
Date: 2024-06-10
Description: Test script to list all available worlds with their descriptions and icons.
"""

from utils.world_loader import (
    WORLD_PRESETS,
    # add_mutant_worlds,
    list_worlds,
    # load_world,
)

worlds = list_worlds()

print("\n🌍 Available Worlds:\n")

for idx, name in enumerate(worlds, start=1):
    preset = WORLD_PRESETS[name]
    icon = preset.get("icon", "")
    desc = preset.get("description", "No description provided.")
    print(f"{idx}. {icon} {name:<23} — {desc}")

# Filepath: /home/jtk/Dev/TerminalLifeform/src/tests/test_list_worlds.py
