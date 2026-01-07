# src/forest_stand_generator/stand.py

import numpy as np
from typing import List, Dict, Optional, Union
from .tree import generate_tree


def generate_stand(
    plot_width: float,
    plot_length: float,
    n_trees: int,
    placement: str = "uniform",
    tree_params: Optional[Union[Dict, List[Dict]]] = None,
    min_spacing: float = 1.0
) -> List[Dict]:
    """
    Generate a forest stand (collection of trees) on a rectangular plot.

    Parameters
    ----------
    plot_width : float
        Width of the rectangular plot (x-direction, in meters or desired units).
    plot_length : float
        Length of the rectangular plot (y-direction, in meters or desired units).
    n_trees : int
        Total number of trees to generate.
    placement : str, optional
        Placement strategy for trees. Options:
        - "uniform": trees are placed in a regular grid across the plot.
        - "random": trees are placed randomly with minimum spacing enforced.
        Default is "uniform".
    tree_params : dict or list of dict, optional
        Parameters for tree generation, passed to `generate_tree`.
        - dict: same parameters applied to all trees.
        - list of dicts: a separate parameter set for each tree. Length must equal n_trees.
        Default is None (empty dict for all trees).
    min_spacing : float, optional
        Minimum distance between trees (only used for "random" placement). Default is 1.0.

    Returns
    -------
    List[Dict]
        List of tree dictionaries, each representing a generated tree with its position and attributes.

    Notes
    -----
    - For "uniform" placement, the function tries to arrange trees in a grid as close to square as possible.
    - For "random" placement, if the requested number of trees cannot fit with the given `min_spacing`, 
      fewer trees may be generated, and a warning is printed.
    - The z-coordinate of all tree positions is set to 0.0 by default.
    """
    if tree_params is None:
        tree_params = {}

    # Detect per-tree parameter list
    per_tree_params = isinstance(tree_params, list)
    if per_tree_params and len(tree_params) != n_trees:
        raise ValueError(
            "When tree_params is a list, its length must equal n_trees"
        )

    tree_list = []

    def get_tree_params(i):
        return tree_params[i] if per_tree_params else tree_params

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
                tree = generate_tree(position=position, **get_tree_params(count))
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
                position = [x, y, 0.0]
                positions.append(position)

                idx = len(tree_list)
                tree = generate_tree(position=position, **get_tree_params(idx))
                tree_list.append(tree)
            attempts += 1

        if len(positions) < n_trees:
            print(f"Warning: Only {len(tree_list)} trees placed due to spacing constraints.")

    else:
        raise ValueError("Unsupported placement type. Choose 'uniform' or 'random'.")

    return tree_list
