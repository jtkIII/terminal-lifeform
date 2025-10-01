# plot_traits.py
import json

import matplotlib.pyplot as plt

with open("logs/trait_evolution.json") as f:
    data = json.load(f)

epochs = [d["epoch"] for d in data]

plt.figure(figsize=(10, 6))
for key in [
    "avg_resilience",
    "avg_metabolism_rate",
    "avg_reproduction_chance",
    "avg_health",
    "avg_energy",
]:
    plt.plot(epochs, [d[key] for d in data], label=key)

plt.xlabel("Epoch")
plt.ylabel("Average Trait Value")
plt.title("Trait Evolution Over Time")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("logs/trait_plot.png", dpi=200)
print("✅ Plot saved as logs/trait_plot.png")
