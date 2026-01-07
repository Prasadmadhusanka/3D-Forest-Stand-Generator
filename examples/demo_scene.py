# examples/demo_scene.py

from forest_stand_generator.stand import generate_stand
from forest_stand_generator.visualization import export_forest_stand_to_csv, plot_forest_stand_plotly
import json

# with open("trees.json") as f:
#     tree_params_list = json.load(f)


# Generate forest stand
stand = generate_stand(
    plot_width=20,
    plot_length=20,
    n_trees= 20,
    placement='random',
    tree_params=  {
      "trunk_height": 4.5,
      "trunk_radius": 0.18,
      "crown_shape": "sphere",
      "crown_height": 3.0,
      "crown_radius": 2.0,
      "lai": 2.5,
      "leaf_radius": 0.09,
      "leaf_angle_distribution": "planophile"
    }
)




# Visualize
plot_forest_stand_plotly(stand)

# Export to CSV
# export_forest_stand_to_csv(stand, "forest_stand.csv")
