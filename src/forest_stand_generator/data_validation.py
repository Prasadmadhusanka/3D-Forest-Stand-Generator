# src/forest_stand_generator/data_validation.py

def validate_tree_params(tree_params_list):
    """
    Validate a list of tree parameter dictionaries loaded from JSON.

    This function ensures that:
      1. The input is a list of dictionaries.
      2. Each dictionary contains all required keys for tree generation.
      3. All numeric parameters have valid, non-negative or positive values.
      4. Categorical parameters (crown shape and leaf angle distribution) are valid.
      5. Leaf radius parameters are valid (mean > 0, sd >=0, min <= max, mean in [min, max]).

    Raises
    ------
    ValueError
        If any validation check fails. The error message indicates the tree index
        and the specific parameter that is invalid.

    Parameters
    ----------
    tree_params_list : list
        List of dictionaries, each representing the parameters for a single tree.
        Each dictionary must include:
            - trunk_height: float > 0
            - trunk_radius: float > 0
            - crown_shape: str, one of "sphere", "sphere_w_LH", "cylinder", "cone"
            - crown_height: float > 0
            - crown_radius: float > 0
            - lai: float >= 0
            - leaf_radius_params: dict with keys "mean", "sd", "min", "max"
            - leaf_angle_distribution: str, one of "uniform", "spherical", "planophile", "erectophile"
    """

    # Define valid options for categorical parameters
    allowed_crown_shapes = {"sphere", "sphere_w_LH", "cylinder", "cone"}
    allowed_leaf_distributions = {"uniform", "spherical", "planophile", "erectophile"}

    # Ensure the input is a list
    if not isinstance(tree_params_list, list):
        raise ValueError("tree_params_list must be a list of dictionaries")

    # Loop through each tree parameter dictionary
    for idx, params in enumerate(tree_params_list):
        # Ensure each item is a dictionary
        if not isinstance(params, dict):
            raise ValueError(f"Tree params at index {idx} must be a dictionary")

        # Check that all required keys exist
        required_keys = [
            "trunk_height", "trunk_radius", "crown_shape",
            "crown_height", "crown_radius", "lai",
            "leaf_radius_params", "leaf_angle_distribution"
        ]
        for key in required_keys:
            if key not in params:
                raise ValueError(f"Missing key '{key}' in tree params at index {idx}")

        # Numeric value validation
        if params["trunk_height"] <= 0:
            raise ValueError(f"trunk_height must be > 0 at index {idx}")
        if params["trunk_radius"] <= 0:
            raise ValueError(f"trunk_radius must be > 0 at index {idx}")
        if params["crown_height"] <= 0:
            raise ValueError(f"crown_height must be > 0 at index {idx}")
        if params["crown_radius"] <= 0:
            raise ValueError(f"crown_radius must be > 0 at index {idx}")
        if params["lai"] < 0:
            raise ValueError(f"lai must be >= 0 at index {idx}")

        # Categorical value validation
        if params["crown_shape"] not in allowed_crown_shapes:
            raise ValueError(
                f"Invalid crown_shape '{params['crown_shape']}' at index {idx}"
            )
        if params["leaf_angle_distribution"] not in allowed_leaf_distributions:
            raise ValueError(
                f"Invalid leaf_angle_distribution '{params['leaf_angle_distribution']}' at index {idx}"
            )
        # Dependency rule: if crown_shape is 'sphere', trunk_height > crown_radius
        if params["crown_shape"] == "sphere" and params["trunk_height"] <= params["crown_radius"]:
            raise ValueError(
                f"For crown_shape 'sphere', trunk_height ({params['trunk_height']}) "
                f"must be greater than crown_radius ({params['crown_radius']}) at index {idx}"
            )
        # --- Validate leaf_radius_params ---
        leaf_params = params["leaf_radius_params"]
        if not isinstance(leaf_params, dict):
            raise ValueError(f"leaf_radius_params must be a dictionary at index {idx}")

        for key in ["mean", "sd", "min", "max"]:
            if key not in leaf_params:
                raise ValueError(f"Missing '{key}' in leaf_radius_params at index {idx}")
            if not isinstance(leaf_params[key], (int, float)):
                raise ValueError(f"leaf_radius_params['{key}'] must be a number at index {idx}")

        if leaf_params["mean"] <= 0:
            raise ValueError(f"leaf_radius_params['mean'] must be > 0 at index {idx}")
        if leaf_params["sd"] < 0:
            raise ValueError(f"leaf_radius_params['sd'] must be >= 0 at index {idx}")
        if leaf_params["min"] <= 0 or leaf_params["max"] <= 0:
            raise ValueError(f"leaf_radius_params['min'] and ['max'] must be > 0 at index {idx}")
        if leaf_params["min"] > leaf_params["max"]:
            raise ValueError(f"leaf_radius_params['min'] cannot be greater than ['max'] at index {idx}")
        if not (leaf_params["min"] <= leaf_params["mean"] <= leaf_params["max"]):
            raise ValueError(f"leaf_radius_params['mean'] must be between ['min'] and ['max'] at index {idx}")




def validate_stand_params(plot_width, plot_length, n_trees, placement, tree_params_list, min_spacing=None):
    """
    Validate all parameters required for generating a forest stand.

    This function performs comprehensive validation to ensure that the forest stand
    generation will not fail due to invalid or nonsensical inputs. It checks:

      1. Plot dimensions (width and length) are positive.
      2. Number of trees (n_trees) is non-negative.
      3. Tree placement type is either 'uniform' or 'random'.
      4. If placement is 'random', minimum spacing between trees (min_spacing) is positive.
      5. Each tree's parameters in tree_params_list are valid (calls `validate_tree_params`).

    Raises
    ------
    ValueError
        If any of the following conditions are violated:
          - plot_width or plot_length is <= 0
          - n_trees < 0
          - placement is not 'uniform' or 'random'
          - min_spacing <= 0 when placement='random'
          - Any tree parameter in tree_params_list is invalid

    Parameters
    ----------
    plot_width : float
        Width of the rectangular plot (x-axis). Must be > 0.
    plot_length : float
        Length of the rectangular plot (y-axis). Must be > 0.
    n_trees : int
        Number of trees to generate. Must be >= 0.
    placement : str
        Tree placement strategy. Must be either:
          - 'uniform': trees arranged in a regular grid
          - 'random': trees placed randomly with minimum spacing enforced
    tree_params_list : list
        List of dictionaries, each representing the parameters of a single tree.
        Each dictionary must follow the format validated by `validate_tree_params`.
    min_spacing : float
        Minimum allowed spacing between trees (used only if placement='random').
        Must be > 0 when placement='random'.
    """

    # Validate plot dimensions
    if plot_width <= 0:
        raise ValueError("plot_width must be positive")
    if plot_length <= 0:
        raise ValueError("plot_length must be positive")

    # Validate number of trees
    if n_trees < 0:
        raise ValueError("n_trees must be >= 0")

    # Validate placement type
    allowed_placements = {"uniform", "random"}
    if placement not in allowed_placements:
        raise ValueError(f"placement must be 'uniform' or 'random', got '{placement}'")

    # tree_params_list validation
    if not isinstance(tree_params_list, list) or len(tree_params_list) == 0:
        raise ValueError("tree_params_list must be a non-empty list of dictionaries")

    if len(tree_params_list) != n_trees:
        raise ValueError(
            f"Number of trees (n_trees={n_trees}) must be equal to "
            f"the length of tree_params_list ({len(tree_params_list)})"
        )

    # Validate min_spacing ONLY if placement is random
    if placement == "random":
        if min_spacing is None:
            raise ValueError(
                "min_spacing must be provided when placement='random'"
            )
        if min_spacing <= 0:
            raise ValueError(
                "min_spacing must be > 0 when placement='random'"
            )

    # Validate per-tree parameters using the previously defined function
    validate_tree_params(tree_params_list)



def validate_plot(plot_width, plot_length):
    if plot_width <= 0 or plot_length <= 0:
        raise ValueError("Plot width and length must be positive numbers.")