# src/forest_stand_generator/stand.py

import numpy as np
from typing import List, Dict, Optional, Union
from .data_validation import validate_stand_params
from .tree import generate_tree


def generate_stand(
    plot_width: float,
    plot_length: float,
    n_trees: int,
    placement: str,
    min_spacing: float,
    tree_params: Union[Dict, List[Dict]],
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
    placement : str
        Placement strategy for trees. Options:
        - "uniform": trees are placed on a regular grid. Grid spacing is validated
          to ensure that tree trunk circles on the ground do not intersect.
        - "random": trees are placed randomly while enforcing minimum spacing
          between trunk centers and preventing trunk overlap.
    min_spacing : float
        Minimum allowed distance between tree centers when placement="random".
        The actual enforced distance between two trees is:
            max(min_spacing, r1 + r2),
        where r1 and r2 are the trunk radii of the two trees.
        Ignored when placement="uniform".
    tree_params : dict or list of dict
        Parameters for tree generation, passed to `generate_tree`.
        - dict: the same parameters are applied to all trees.
        - list of dicts: a separate parameter set for each tree.
          Length must equal n_trees.

    Returns
    -------
    List[Dict]
        List of tree dictionaries. Each dictionary represents a generated tree
        with its spatial position and structural attributes.

    Notes
    -----
    - Tree positions represent the center of the trunk at ground level
      (x, y, z = 0.0).
    - For both placement modes, tree trunk circles on the ground are guaranteed
      not to intersect.
    - For "uniform" placement, a ValueError is raised if the plot is too small
      to accommodate all trees without trunk overlap.
    - For "random" placement, if the requested number of trees cannot be placed
      due to spacing constraints, fewer trees may be generated and a warning
      is printed.
    """

    # Normalize tree_params
    if isinstance(tree_params, dict):
        tree_params_list = [tree_params for _ in range(n_trees)]
    elif isinstance(tree_params, list):
        tree_params_list = tree_params
    else:
        raise ValueError(
            "tree_params must be a dict or a list of dicts"
        )

    validate_stand_params(
        plot_width=plot_width,
        plot_length=plot_length,
        n_trees=n_trees,
        placement=placement,
        tree_params_list=tree_params_list,
        min_spacing=min_spacing
    )

    tree_list = []

    def get_tree_params(i):
        return tree_params_list[i]

    # UNIFORM PLACEMENT (radius-aware)
    if placement == "uniform":

        # compute maximum trunk radius
        radii = [params["trunk_radius"] for params in tree_params_list]
        max_radius = max(radii)
        min_required_spacing = 2 * max_radius

        # Grid layout
        n_cols = int(np.ceil(np.sqrt(n_trees * plot_width / plot_length)))
        n_rows = int(np.ceil(n_trees / n_cols))
        x_spacing = plot_width / n_cols
        y_spacing = plot_length / n_rows

        # enforce no trunk overlap
        if x_spacing < min_required_spacing or y_spacing < min_required_spacing:
            raise ValueError(
                "Uniform placement failed: plot too small to avoid trunk area overlap."
            )

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

    # RANDOM PLACEMENT (radius-aware)
    elif placement == "random":

        attempts = 0
        max_attempts = n_trees * 50
        positions = []
        radii = []

        while len(positions) < n_trees and attempts < max_attempts:
            x = np.random.uniform(0, plot_width)
            y = np.random.uniform(0, plot_length)
            pos = np.array([x, y])

            idx = len(tree_list)
            new_radius = get_tree_params(idx)["trunk_radius"]

            # radius-aware distance check
            valid = True
            for p, r in zip(positions, radii):
                d = np.linalg.norm(pos - np.array(p[:2]))
                required = max(min_spacing, new_radius + r)
                if d < required:
                    valid = False
                    break

            if valid:
                position = [x, y, 0.0]
                positions.append(position)
                radii.append(new_radius)

                tree = generate_tree(position=position, **get_tree_params(idx))
                tree_list.append(tree)

            attempts += 1

        if len(tree_list) < n_trees:
            print(
                f"Warning: Only {len(tree_list)} trees placed due to spacing constraints."
            )

    else:
        raise ValueError("Unsupported placement type. Choose 'uniform' or 'random'.")

    return tree_list
