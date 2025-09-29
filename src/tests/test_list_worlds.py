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
