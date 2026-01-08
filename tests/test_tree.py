# tests/test_tree.py

# ==============================================================
# IMPORTS
# ==============================================================

import numpy as np
import pytest
from forest_stand_generator.tree import (
    sample_leaf_normal,
    sample_point_in_crown,
    generate_tree,
)

# Shared leaf radius parameters for generate_tree tests
leaf_radius_params = {"mean": 0.05, "sd": 0.01, "min": 0.01, "max": 0.1}


# ==============================================================
# SAMPLE_LEAF_NORMAL TESTS
# ==============================================================


def test_uniform_returns_unit_vector():
    """'uniform' distribution returns a valid 3D unit vector."""
    v = sample_leaf_normal("uniform")
    assert isinstance(v, np.ndarray)
    assert v.shape == (3,)
    np.testing.assert_allclose(np.linalg.norm(v), 1.0, rtol=1e-6)


def test_spherical_returns_unit_vector():
    """'spherical' distribution returns a valid 3D unit vector."""
    v = sample_leaf_normal("spherical")
    assert isinstance(v, np.ndarray)
    assert v.shape == (3,)
    np.testing.assert_allclose(np.linalg.norm(v), 1.0, rtol=1e-6)


def test_uniform_is_random():
    """Successive 'uniform' samples are not deterministic."""
    v1 = sample_leaf_normal("uniform")
    v2 = sample_leaf_normal("uniform")
    assert not np.allclose(v1, v2)


def test_planophile_direction():
    """'planophile' distribution returns fixed vector pointing up (z-axis)."""
    v = sample_leaf_normal("planophile")
    expected = np.array([0.0, 0.0, 1.0])
    np.testing.assert_array_equal(v, expected)


def test_erectophile_direction():
    """'erectophile' distribution returns fixed vector along x-axis."""
    v = sample_leaf_normal("erectophile")
    expected = np.array([1.0, 0.0, 0.0])
    np.testing.assert_array_equal(v, expected)


def test_unknown_distribution_raises_error():
    """Unsupported leaf distribution raises ValueError."""
    with pytest.raises(ValueError):
        sample_leaf_normal("unknown")


# ==============================================================
# SAMPLE_POINT_IN_CROWN TESTS
# ==============================================================


def test_sphere_point_inside_volume():
    """Points sampled in a spherical crown are within radius and height."""
    radius = 2.0
    height = 6.0
    p = sample_point_in_crown("sphere", height, radius)
    assert np.linalg.norm(p[:2]) <= radius
    assert -height <= p[2] <= height


def test_sphere_w_lh_upper_hemisphere_only():
    """'sphere_w_LH' samples points only in upper hemisphere."""
    radius = 2.0
    height = 5.0
    p = sample_point_in_crown("sphere_w_LH", height, radius)
    assert p[2] >= 0.0
    assert np.linalg.norm(p[:2]) <= radius
    assert p[2] <= height


def test_cylinder_point_inside_volume():
    """Points in cylinder crown are within radius and height."""
    radius = 1.5
    height = 4.0
    p = sample_point_in_crown("cylinder", height, radius)
    assert np.linalg.norm(p[:2]) <= radius
    assert 0.0 <= p[2] <= height


def test_cone_point_inside_volume():
    """Points in cone crown are within tapering radius and height."""
    radius = 3.0
    height = 6.0
    p = sample_point_in_crown("cone", height, radius)
    z = p[2]
    r_xy = np.linalg.norm(p[:2])
    r_max = radius * (1 - z / height)
    assert 0.0 <= z <= height
    assert r_xy <= r_max + 1e-12  # numerical tolerance


def test_multiple_samples_are_valid():
    """Multiple stochastic samples remain within cylinder bounds."""
    radius = 2.0
    height = 5.0
    for _ in range(1000):
        p = sample_point_in_crown("cylinder", height, radius)
        assert np.linalg.norm(p[:2]) <= radius
        assert 0.0 <= p[2] <= height


def test_unknown_shape_raises_error():
    """Unsupported crown shape raises ValueError."""
    with pytest.raises(ValueError):
        sample_point_in_crown("pyramid", height=5.0, radius=2.0)


# ==============================================================
# GENERATE_TREE TESTS
# ==============================================================


def test_generate_tree_structure():
    """Tree has top-level 'trunk' and 'leaves' keys and correct types."""
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=2.0,
        lai=2.0,
        leaf_radius_params=leaf_radius_params,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 0.0],
    )
    assert "trunk" in tree
    assert "leaves" in tree
    assert isinstance(tree["trunk"], dict)
    assert isinstance(tree["leaves"], list)


def test_generate_tree_trunk_properties():
    """Verify trunk height, radius, and base position."""
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.3,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius_params=leaf_radius_params,
        leaf_angle_distribution="planophile",
        position=[1.0, 2.0, 0.0],
    )
    trunk = tree["trunk"]
    assert trunk["height"] == 5.0
    assert trunk["radius"] == 0.3
    np.testing.assert_array_equal(trunk["base"], np.array([1.0, 2.0, 0.0]))


def test_generate_tree_leaves_positions_within_crown():
    """All leaves lie inside crown bounds above the trunk."""
    crown_height = 4.0
    crown_radius = 2.0
    trunk_height = 5.0
    tree = generate_tree(
        trunk_height=trunk_height,
        trunk_radius=0.2,
        crown_shape="cylinder",
        crown_height=crown_height,
        crown_radius=crown_radius,
        lai=1.0,
        leaf_radius_params=leaf_radius_params,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 0.0],
    )
    for leaf in tree["leaves"]:
        x, y, z = leaf["center"]
        r_xy = np.sqrt(x**2 + y**2)
        assert 0 <= z <= trunk_height + crown_height
        assert r_xy <= crown_radius


def test_generate_tree_leaves_normals():
    """Leaf normals are unit vectors."""
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="cone",
        crown_height=4.0,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius_params=leaf_radius_params,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 0.0],
    )
    for leaf in tree["leaves"]:
        normal = leaf["normal"]
        assert isinstance(normal, np.ndarray)
        np.testing.assert_allclose(np.linalg.norm(normal), 1.0, rtol=1e-6)


def test_generate_tree_leaf_radius_within_bounds():
    """All leaf radii are within min/max bounds."""
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius_params=leaf_radius_params,
        leaf_angle_distribution="spherical",
        position=[0.0, 0.0, 0.0],
    )
    for leaf in tree["leaves"]:
        r = leaf["radius"]
        assert leaf_radius_params["min"] <= r <= leaf_radius_params["max"]


def test_generate_tree_number_of_leaves_matches_lai():
    """Number of leaves matches LAI calculation."""
    crown_radius = 2.0
    lai = 1.5
    mean_leaf_radius = leaf_radius_params["mean"]
    expected_n_leaves = int(
        lai * np.pi * crown_radius**2 / (np.pi * mean_leaf_radius**2)
    )
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=crown_radius,
        lai=lai,
        leaf_radius_params=leaf_radius_params,
        leaf_angle_distribution="planophile",
        position=[0.0, 0.0, 0.0],
    )
    assert len(tree["leaves"]) == expected_n_leaves
