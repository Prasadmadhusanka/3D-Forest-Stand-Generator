# examples/demo_scene.py

import json
from pathlib import Path
from forest_stand_generator.stand import generate_stand
from forest_stand_generator.visualization import plot_forest_stand, plot_forest_top_view
from forest_stand_generator.export import export_forest_stand_to_csv, export_forest_stand_to_json

# Path to this file's directory
HERE = Path(__file__).resolve().parent

# Load per-tree parameters from JSON
json_path = HERE / "trees06.json"
with open(json_path, "r") as f:
    tree_params_list = json.load(f)


# Generate forest stand
stand = generate_stand(
    plot_width=20,
    plot_length=20,
    n_trees=len(tree_params_list),
    placement='random',
    tree_params=tree_params_list
)


# Visualize as 3D
plot_forest_stand(stand)

# Visualize as 2D (top View)
# plot_forest_top_view(stand)

# Export to CSV
export_forest_stand_to_csv(stand, "forest_stand.csv")

# Export to JSON
export_forest_stand_to_json(stand, "forest_stand.json")
