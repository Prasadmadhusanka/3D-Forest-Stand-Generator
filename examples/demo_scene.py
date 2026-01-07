# examples/demo_scene.py

import json
from pathlib import Path
from forest_stand_generator.stand import generate_stand
from forest_stand_generator.visualization import plot_forest_stand_plotly
from forest_stand_generator.export import export_forest_stand_to_csv

# Path to this file's directory
HERE = Path(__file__).resolve().parent

# Load per-tree parameters from JSON
json_path = HERE / "trees.json"
with open(json_path, "r") as f:
    tree_params_list = json.load(f)


# Generate forest stand
stand = generate_stand(
    plot_width=20,
    plot_length=20,
    n_trees=len(tree_params_list),
    placement='uniform',
    tree_params=tree_params_list
)

# import numpy as np
# import json

# class NumpyEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, np.ndarray):
#             return obj.tolist()
#         return super().default(obj)

# json_output_path = HERE / "forest_stand.json"
# with open(json_output_path, "w") as f:
#     json.dump(stand, f, indent=4, cls=NumpyEncoder)

# print(f"Forest stand saved to {json_output_path}")


# Visualize
plot_forest_stand_plotly(stand)

# Export to CSV
# export_forest_stand_to_csv(stand, "forest_stand.csv")
