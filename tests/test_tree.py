# tests/test_tree.py

import numpy as np
import pytest


from forest_stand_generator.tree import sample_leaf_normal


def test_uniform_returns_unit_vector():
    """
    Verify that the 'uniform' leaf angle distribution returns a valid
    3D unit vector.

    The sampled vector should:
    - Be a NumPy array
    - Have shape (3,)
    - Have unit length (norm ≈ 1)
    """
    v = sample_leaf_normal("uniform")

    assert isinstance(v, np.ndarray)
    assert v.shape == (3,)
    np.testing.assert_allclose(np.linalg.norm(v), 1.0, rtol=1e-6)


def test_spherical_returns_unit_vector():
    """
    Verify that the 'spherical' leaf angle distribution returns a valid
    3D unit vector.

    The sampled vector should:
    - Be a NumPy array
    - Have shape (3,)
    - Have unit length (norm ≈ 1)
    """
    v = sample_leaf_normal("spherical")

    assert isinstance(v, np.ndarray)
    assert v.shape == (3,)
    np.testing.assert_allclose(np.linalg.norm(v), 1.0, rtol=1e-6)


def test_uniform_is_random():
    """
    Check that successive samples from the 'uniform' distribution
    are not deterministic.

    Two independently sampled vectors should almost never be identical.
    """
    v1 = sample_leaf_normal("uniform")
    v2 = sample_leaf_normal("uniform")

    # Extremely unlikely to be exactly equal if random
    assert not np.allclose(v1, v2)


def test_planophile_direction():
    """
    Verify that the 'planophile' distribution returns a fixed leaf normal
    pointing upward along the z-axis.

    This represents mostly horizontal leaves.
    """
    v = sample_leaf_normal("planophile")

    expected = np.array([0.0, 0.0, 1.0])
    np.testing.assert_array_equal(v, expected)


def test_erectophile_direction():
    """
    Verify that the 'erectophile' distribution returns a fixed leaf normal
    pointing along the x-axis.

    This represents mostly vertical leaves.
    """
    v = sample_leaf_normal("erectophile")

    expected = np.array([1.0, 0.0, 0.0])
    np.testing.assert_array_equal(v, expected)


def test_unknown_distribution_raises_error():
    """
    Verify that providing an unsupported leaf angle distribution
    raises a ValueError.
    """
    with pytest.raises(ValueError):
        sample_leaf_normal("unknown")






from forest_stand_generator.tree import sample_point_in_crown

def test_sphere_point_inside_volume():
    """
    Verify that points sampled in a spherical crown lie within
    the specified radius and height-scaled z-extent.
    """
    radius = 2.0
    height = 6.0

    p = sample_point_in_crown("sphere", height, radius)

    # x-y radius must be within the crown radius
    assert np.linalg.norm(p[:2]) <= radius

    # z must lie within scaled spherical bounds
    assert -height <= p[2] <= height


def test_sphere_w_lh_upper_hemisphere_only():
    """
    Verify that 'sphere_w_LH' only samples points in the upper hemisphere
    (z >= 0) and within the crown radius.
    """
    radius = 2.0
    height = 5.0

    p = sample_point_in_crown("sphere_w_LH", height, radius)

    assert p[2] >= 0.0
    assert np.linalg.norm(p[:2]) <= radius
    assert p[2] <= height


def test_cylinder_point_inside_volume():
    """
    Verify that points sampled in a cylindrical crown lie within
    the circular cross-section and height limits.
    """
    radius = 1.5
    height = 4.0

    p = sample_point_in_crown("cylinder", height, radius)

    # Radial distance must be within cylinder radius
    assert np.linalg.norm(p[:2]) <= radius

    # z must lie within cylinder height
    assert 0.0 <= p[2] <= height


def test_cone_point_inside_volume():
    """
    Verify that points sampled in a conical crown lie within
    the linearly tapering radius at the sampled height.
    """
    radius = 3.0
    height = 6.0

    p = sample_point_in_crown("cone", height, radius)

    z = p[2]
    r_xy = np.linalg.norm(p[:2])
    r_max = radius * (1 - z / height)

    assert 0.0 <= z <= height
    assert r_xy <= r_max + 1e-12  # numerical tolerance


def test_multiple_samples_are_valid():
    """
    Perform multiple samples to ensure no occasional out-of-bound
    values are produced due to stochastic sampling.
    """
    radius = 2.0
    height = 5.0

    for _ in range(1000):
        p = sample_point_in_crown("cylinder", height, radius)
        assert np.linalg.norm(p[:2]) <= radius
        assert 0.0 <= p[2] <= height


def test_unknown_shape_raises_error():
    """
    Verify that providing an unsupported crown shape raises ValueError.
    """
    with pytest.raises(ValueError):
        sample_point_in_crown("pyramid", height=5.0, radius=2.0)





from forest_stand_generator.tree import generate_tree

def test_generate_tree_structure():
    """
    Verify that the generated tree has the correct top-level structure
    and required dictionary keys.
    """
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=2.0,
        lai=2.0,
        leaf_radius=0.05,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 0.0]
    )

    assert "trunk" in tree
    assert "leaves" in tree

    assert isinstance(tree["leaves"], list)
    assert isinstance(tree["trunk"], dict)


def test_trunk_properties():
    """
    Verify trunk geometry and base position are correctly assigned.
    """
    position = [1.0, 2.0, 0.5]
    trunk_height = 6.0
    trunk_radius = 0.3

    tree = generate_tree(
        trunk_height=trunk_height,
        trunk_radius=trunk_radius,
        crown_shape="cylinder",
        crown_height=5.0,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius=0.1,
        leaf_angle_distribution="planophile",
        position=position
    )

    trunk = tree["trunk"]

    np.testing.assert_array_equal(trunk["base"], np.array(position))
    assert trunk["height"] == trunk_height
    assert trunk["radius"] == trunk_radius


def test_number_of_leaves_from_lai():
    """
    Verify that the number of generated leaves matches the expected
    value derived from LAI and crown/leaf areas.
    """
    crown_radius = 2.0
    leaf_radius = 0.1
    lai = 3.0

    crown_area = np.pi * crown_radius**2
    leaf_area = np.pi * leaf_radius**2
    expected_n_leaves = int((lai * crown_area) / leaf_area)

    tree = generate_tree(
        trunk_height=4.0,
        trunk_radius=0.2,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=crown_radius,
        lai=lai,
        leaf_radius=leaf_radius,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 0.0]
    )

    assert len(tree["leaves"]) == expected_n_leaves


def test_leaf_centers_are_above_trunk():
    """
    Verify that all leaves are positioned above the trunk base
    and within the crown vertical extent.
    """
    trunk_height = 5.0
    crown_height = 4.0

    tree = generate_tree(
        trunk_height=trunk_height,
        trunk_radius=0.2,
        crown_shape="cone",
        crown_height=crown_height,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius=0.1,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 1.0]
    )

    crown_base_z = 1.0 + trunk_height

    for leaf in tree["leaves"]:
        z = leaf["center"][2]
        assert crown_base_z <= z <= crown_base_z + crown_height


def test_leaf_normals_are_unit_vectors():
    """
    Verify that all leaf normals are unit vectors regardless of
    the leaf angle distribution.
    """
    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="sphere",
        crown_height=4.0,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius=0.1,
        leaf_angle_distribution="uniform",
        position=[0.0, 0.0, 0.0]
    )

    for leaf in tree["leaves"]:
        n = leaf["normal"]
        np.testing.assert_allclose(np.linalg.norm(n), 1.0, rtol=1e-6)


def test_leaf_radius_is_constant():
    """
    Verify that all generated leaves have the specified leaf radius.
    """
    leaf_radius = 0.08

    tree = generate_tree(
        trunk_height=5.0,
        trunk_radius=0.2,
        crown_shape="cylinder",
        crown_height=4.0,
        crown_radius=2.0,
        lai=1.0,
        leaf_radius=leaf_radius,
        leaf_angle_distribution="erectophile",
        position=[0.0, 0.0, 0.0]
    )

    for leaf in tree["leaves"]:
        assert leaf["radius"] == leaf_radius


def test_invalid_crown_shape_raises_error():
    """
    Verify that providing an unsupported crown shape causes
    the tree generation process to fail with a ValueError.

    This ensures invalid crown geometries are not silently accepted
    and that errors from crown sampling propagate correctly.
    """
    with pytest.raises(ValueError):
        generate_tree(
            trunk_height=5.0,
            trunk_radius=0.2,
            crown_shape="pyramid",
            crown_height=4.0,
            crown_radius=2.0,
            lai=1.0,
            leaf_radius=0.1,
            leaf_angle_distribution="uniform",
            position=[0.0, 0.0, 0.0]
        )


def test_invalid_leaf_angle_distribution_raises_error():
    """
    Verify that providing an unsupported leaf angle distribution
    raises a ValueError during tree generation.

    This ensures that invalid leaf orientation models are rejected
    and that errors from leaf normal sampling propagate correctly.
    """
    with pytest.raises(ValueError):
        generate_tree(
            trunk_height=5.0,
            trunk_radius=0.2,
            crown_shape="sphere",
            crown_height=4.0,
            crown_radius=2.0,
            lai=1.0,
            leaf_radius=0.1,
            leaf_angle_distribution="invalid",
            position=[0.0, 0.0, 0.0]
        )
