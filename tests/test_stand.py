# tests/test_stand.py

# ==============================================================
# IMPORTS
# ==============================================================

import numpy as np
import pytest
from forest_stand_generator.stand import generate_stand


# SHARED TREE PARAMETERS
default_tree_params = {
    "trunk_height": 5.0,
    "trunk_radius": 0.2,
    "crown_shape": "sphere",
    "crown_height": 4.0,
    "crown_radius": 2.0,
    "lai": 1.0,
    "leaf_radius_params": {"mean": 0.1, "sd": 0.01, "min": 0.05, "max": 0.15},
    "leaf_angle_distribution": "uniform",
}

# ==============================================================
# UNIFORM PLACEMENT TESTS
# ==============================================================


def test_generate_stand_returns_correct_number_of_trees():
    """Uniform placement generates the requested number of trees."""
    n_trees = 10
    trees = generate_stand(
        plot_width=10.0,
        plot_length=10.0,
        n_trees=n_trees,
        placement="uniform",
        min_spacing=0.0,  # ignored for uniform
        tree_params=default_tree_params,
    )
    assert isinstance(trees, list)
    assert len(trees) == n_trees


def test_uniform_placement_within_plot_bounds():
    """Trees placed uniformly lie within plot boundaries."""
    plot_width = 8.0
    plot_length = 6.0
    n_trees = 6
    trees = generate_stand(
        plot_width=plot_width,
        plot_length=plot_length,
        n_trees=n_trees,
        placement="uniform",
        min_spacing=0.0,
        tree_params=default_tree_params,
    )
    for tree in trees:
        x, y, z = tree["trunk"]["base"]
        assert 0.0 <= x <= plot_width
        assert 0.0 <= y <= plot_length
        assert z == 0.0


# ==============================================================
# RANDOM PLACEMENT TESTS
# ==============================================================


def test_random_placement_respects_min_spacing():
    """Random placement enforces minimum spacing between trunks."""
    min_spacing = 1.5
    n_trees = 8
    trees = generate_stand(
        plot_width=10.0,
        plot_length=10.0,
        n_trees=n_trees,
        placement="random",
        min_spacing=min_spacing,
        tree_params=default_tree_params,
    )
    positions = [tree["trunk"]["base"][:2] for tree in trees]
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dist = np.linalg.norm(positions[i] - positions[j])
            assert dist >= min_spacing


# ==============================================================
# PER-TREE PARAMETERS TESTS
# ==============================================================


def test_per_tree_parameters_are_applied_correctly():
    """Different per-tree parameters are applied correctly."""
    tree_params_list = [
        {**default_tree_params, "trunk_height": 4.0},
        {**default_tree_params, "trunk_height": 6.0},
    ]
    trees = generate_stand(
        plot_width=5.0,
        plot_length=5.0,
        n_trees=2,
        placement="uniform",
        min_spacing=0.0,
        tree_params=tree_params_list,
    )
    assert trees[0]["trunk"]["height"] == 4.0
    assert trees[1]["trunk"]["height"] == 6.0


# ==============================================================
# ERROR HANDLING TESTS
# ==============================================================


def test_invalid_tree_params_list_length_raises_error():
    """Providing a tree_params list with incorrect length raises ValueError."""
    tree_params_list = [default_tree_params]  # only 1, but n_trees=3
    with pytest.raises(ValueError):
        generate_stand(
            plot_width=10.0,
            plot_length=10.0,
            n_trees=3,
            placement="uniform",
            min_spacing=0.0,
            tree_params=tree_params_list,
        )


def test_invalid_placement_type_raises_error():
    """Unsupported placement type raises ValueError."""
    with pytest.raises(ValueError):
        generate_stand(
            plot_width=10.0,
            plot_length=10.0,
            n_trees=5,
            placement="hexagonal",
            min_spacing=0.0,
            tree_params=default_tree_params,
        )
