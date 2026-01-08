# examples/demo_scene.py

import json
from pathlib import Path
from forest_stand_generator.stand import generate_stand
from forest_stand_generator.visualization import plot_forest_stand, plot_forest_top_view
from forest_stand_generator.export import (
    export_forest_stand_to_csv,
    export_forest_stand_to_json,
)

# Path to this file's directory
HERE = Path(__file__).resolve().parent

# Load per-tree parameters from JSON
json_path = HERE / "10_trees.json"
with open(json_path, "r") as f:
    tree_params_list = json.load(f)


# Define stand parameters
PLOT_WIDTH = 20
PLOT_LENGTH = 20
NO_OF_TREES = len(tree_params_list)  # Only change this if tree_params_list is a dict
PLACEMENT = "uniform"
MIN_SPACING = 1.0  # only needed if PLACEMENT = "random"
TREE_PARAMS_LIST = tree_params_list  # List of tree parameter dictionaries


# Generate forest stand
stand = generate_stand(
    plot_width=PLOT_WIDTH,
    plot_length=PLOT_LENGTH,
    n_trees=NO_OF_TREES,
    placement=PLACEMENT,
    tree_params=TREE_PARAMS_LIST,
    min_spacing=MIN_SPACING,
)


# Visualize as 3D
plot_forest_stand(stand, plot_width=PLOT_WIDTH, plot_length=PLOT_LENGTH)

# Visualize as 2D (top View)
plot_forest_top_view(stand, plot_width=PLOT_WIDTH, plot_length=PLOT_LENGTH)

# Export to CSV
export_forest_stand_to_csv(stand, "forest_stand.csv")

# Export to JSON
export_forest_stand_to_json(stand, "forest_stand.json")
