#!/usr/bin/env python3
"""
plot_summary.py - Generate simulation summary plots from sim_totals.json and trait_tracker.json
"""

import json
import os
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

# --- File paths ---
SIM_TOTALS_FILE = "logs/sim_totals.json"
TRAIT_TRACKER_FILE = "logs/trait_tracker.json"
OUTPUT_FILE = "plots/summary.png"

os.makedirs("plots", exist_ok=True)

# --- Load sim_totals ---
with open(SIM_TOTALS_FILE) as f:
    sim_totals = json.load(f)

# Aggregate by world
world_stats = defaultdict(lambda: defaultdict(list))
for run in sim_totals:
    w = run["world_name"]
    world_stats[w]["alive"].append(run.get("total_alive_at_conclusion", 0))
    world_stats[w]["thriving"].append(run.get("total_thriving", 0))
    world_stats[w]["struggling"].append(run.get("total_struggling", 0))
    world_stats[w]["births"].append(run.get("total_births", 0))
    world_stats[w]["deaths"].append(run.get("total_deaths", 0))
    world_stats[w]["mutations"].append(run.get("total_mutations", 0))
    world_stats[w]["max_entities"].append(run.get("max_entities", 0))

# Compute means per world
aggregated = {}
for world, stats in world_stats.items():
    aggregated[world] = {k: np.mean(v) for k, v in stats.items()}

# --- Load trait_tracker ---
with open(TRAIT_TRACKER_FILE) as f:
    traits = json.load(f)

# --- Plotting ---
fig, axs = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle("Terminal Lifeform Simulation Summary", fontsize=18, weight="bold")

# === Panel 1: Population outcomes by world ===
worlds = list(aggregated.keys())
alive_means = [aggregated[w]["alive"] for w in worlds]
thriving_means = [aggregated[w]["thriving"] for w in worlds]
struggling_means = [aggregated[w]["struggling"] for w in worlds]

x = np.arange(len(worlds))
width = 0.25

axs[0].bar(x - width, alive_means, width, label="Alive (end)")
axs[0].bar(x, thriving_means, width, label="Thriving")
axs[0].bar(x + width, struggling_means, width, label="Struggling")

axs[0].set_ylabel("Entities (avg per run)")
axs[0].set_title("Population Outcomes by World")
axs[0].set_xticks(x)
axs[0].set_xticklabels(worlds, rotation=30, ha="right")
axs[0].legend()
axs[0].grid(axis="y", linestyle="--", alpha=0.6)

# === Panel 2: Trait averages (global) ===
trait_labels = [
    "avg_resilience",
    "avg_metabolism_rate",
    "avg_reproduction_chance",
    "avg_health",
    "avg_energy",
    "avg_population",
]
trait_values = [traits.get(t, 0) for t in trait_labels]

axs[1].bar(trait_labels, trait_values, color="teal")
axs[1].set_ylabel("Value (avg)")
axs[1].set_title("Average Traits Across All Runs")
axs[1].tick_params(axis="x", rotation=30)
axs[1].grid(axis="y", linestyle="--", alpha=0.6)

plt.tight_layout(rect=[0, 0, 1, 0.96])  # type: ignore
plt.savefig(OUTPUT_FILE, dpi=150)
print(f"✅ Summary plot saved to: {OUTPUT_FILE}")
