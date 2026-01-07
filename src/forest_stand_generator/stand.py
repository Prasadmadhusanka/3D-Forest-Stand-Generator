# src/forest_stand_generator/stand.py

import numpy as np
from typing import List, Dict, Optional
from .tree import generate_tree

def generate_stand(
    plot_width: float,
    plot_length: float,
    n_trees: int,
    placement: str = "uniform",
    tree_params: Optional[Dict] = None,
    min_spacing: float = 1.0
) -> List[Dict]:
    """
    Generate a forest stand (collection of trees) on a rectangular plot.

    Parameters
    ----------
    plot_width : float
        Width of the rectangular plot (x-direction)
    plot_length : float
        Length of the rectangular plot (y-direction)
    n_trees : int
        Number of trees to generate
    placement : str
        "uniform" or "random" placement
    tree_params : dict
        Per-tree parameters to pass to generate_tree()
    min_spacing : float
        Minimum distance between trees (used for random placement)

    Returns
    -------
    List[Dict]
        List of tree dictionaries
    """

    if tree_params is None:
        tree_params = {}

    tree_list = []

    if placement == "uniform":
        # Determine grid size (closest to square)
        n_cols = int(np.ceil(np.sqrt(n_trees * plot_width / plot_length)))
        n_rows = int(np.ceil(n_trees / n_cols))
        x_spacing = plot_width / n_cols
        y_spacing = plot_length / n_rows

        count = 0
        for i in range(n_cols):
            for j in range(n_rows):
                if count >= n_trees:
                    break
                x = x_spacing * (i + 0.5)
                y = y_spacing * (j + 0.5)
                position = [x, y, 0.0]
                tree = generate_tree(position=position, **tree_params)
                tree_list.append(tree)
                count += 1

    elif placement == "random":
        attempts = 0
        max_attempts = n_trees * 50
        positions = []

        while len(positions) < n_trees and attempts < max_attempts:
            x = np.random.uniform(0, plot_width)
            y = np.random.uniform(0, plot_length)
            pos = np.array([x, y])
            if all(np.linalg.norm(pos - np.array(p[:2])) >= min_spacing for p in positions):
                positions.append([x, y, 0.0])
                tree = generate_tree(position=[x, y, 0.0], **tree_params)
                tree_list.append(tree)
            attempts += 1

        if len(positions) < n_trees:
            print(f"Warning: Only {len(positions)} trees placed due to spacing constraints.")

    else:
        raise ValueError("Unsupported placement type. Choose 'uniform' or 'random'.")

    return tree_list