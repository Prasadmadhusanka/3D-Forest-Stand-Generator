# tests/test_stand.py

import numpy as np
import pytest

from forest_stand_generator.stand import generate_stand

def test_generate_stand_returns_correct_number_of_trees():
    """
    Verify that the requested number of trees is generated
    for uniform placement.
    """
    n_trees = 10

    trees = generate_stand(
        plot_width=10.0,
        plot_length=10.0,
        n_trees=n_trees,
        placement="uniform",
        tree_params={
            "trunk_height": 5.0,
            "trunk_radius": 0.2,
            "crown_shape": "sphere",
            "crown_height": 4.0,
            "crown_radius": 2.0,
            "lai": 1.0,
            "leaf_radius": 0.1,
            "leaf_angle_distribution": "uniform",
        }
    )

    assert isinstance(trees, list)
    assert len(trees) == n_trees


def test_uniform_placement_within_plot_bounds():
    """
    Verify that trees placed using uniform placement lie within
    the plot boundaries.
    """
    plot_width = 8.0
    plot_length = 6.0

    trees = generate_stand(
        plot_width=plot_width,
        plot_length=plot_length,
        n_trees=6,
        placement="uniform",
        tree_params={
            "trunk_height": 4.0,
            "trunk_radius": 0.2,
            "crown_shape": "cylinder",
            "crown_height": 3.0,
            "crown_radius": 1.5,
            "lai": 1.0,
            "leaf_radius": 0.1,
            "leaf_angle_distribution": "planophile",
        }
    )

    for tree in trees:
        x, y, z = tree["trunk"]["base"]
        assert 0.0 <= x <= plot_width
        assert 0.0 <= y <= plot_length
        assert z == 0.0


def test_random_placement_respects_min_spacing():
    """
    Verify that random placement enforces the minimum spacing
    constraint between trees.
    """
    min_spacing = 1.5

    trees = generate_stand(
        plot_width=10.0,
        plot_length=10.0,
        n_trees=10,
        placement="random",
        min_spacing=min_spacing,
        tree_params={
            "trunk_height": 5.0,
            "trunk_radius": 0.2,
            "crown_shape": "sphere",
            "crown_height": 4.0,
            "crown_radius": 2.0,
            "lai": 1.0,
            "leaf_radius": 0.1,
            "leaf_angle_distribution": "uniform",
        }
    )

    positions = [tree["trunk"]["base"][:2] for tree in trees]

    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dist = np.linalg.norm(positions[i] - positions[j])
            assert dist >= min_spacing



def test_per_tree_parameters_are_applied_correctly():
    """
    Verify that a list of per-tree parameter dictionaries is
    correctly applied to each generated tree.
    """
    tree_params = [
        {
            "trunk_height": 4.0,
            "trunk_radius": 0.2,
            "crown_shape": "sphere",
            "crown_height": 3.0,
            "crown_radius": 1.5,
            "lai": 1.0,
            "leaf_radius": 0.1,
            "leaf_angle_distribution": "uniform",
        },
        {
            "trunk_height": 6.0,
            "trunk_radius": 0.3,
            "crown_shape": "cone",
            "crown_height": 4.0,
            "crown_radius": 2.0,
            "lai": 2.0,
            "leaf_radius": 0.1,
            "leaf_angle_distribution": "planophile",
        },
    ]

    trees = generate_stand(
        plot_width=5.0,
        plot_length=5.0,
        n_trees=2,
        placement="uniform",
        tree_params=tree_params
    )

    assert trees[0]["trunk"]["height"] == 4.0
    assert trees[1]["trunk"]["height"] == 6.0



def test_invalid_tree_params_list_length_raises_error():
    """
    Verify that providing a list of tree parameters with incorrect
    length raises a ValueError.
    """
    with pytest.raises(ValueError):
        generate_stand(
            plot_width=10.0,
            plot_length=10.0,
            n_trees=3,
            placement="uniform",
            tree_params=[
                {
                    "trunk_height": 5.0,
                    "trunk_radius": 0.2,
                    "crown_shape": "sphere",
                    "crown_height": 4.0,
                    "crown_radius": 2.0,
                    "lai": 1.0,
                    "leaf_radius": 0.1,
                    "leaf_angle_distribution": "uniform",
                }
            ]
        )



def test_invalid_placement_type_raises_error():
    """
    Verify that an unsupported placement strategy raises a ValueError.
    """
    with pytest.raises(ValueError):
        generate_stand(
            plot_width=10.0,
            plot_length=10.0,
            n_trees=5,
            placement="hexagonal",
            tree_params={
                "trunk_height": 5.0,
                "trunk_radius": 0.2,
                "crown_shape": "sphere",
                "crown_height": 4.0,
                "crown_radius": 2.0,
                "lai": 1.0,
                "leaf_radius": 0.1,
                "leaf_angle_distribution": "uniform",
            }
        )
