# src/forest_stand_generator/tree.py

import numpy as np
from typing import Dict, List



import numpy as np

def sample_leaf_normal(distribution: str) -> np.ndarray:
    """
        Sample a 3D leaf normal vector according to a specified leaf angle distribution.

        The leaf normal vector represents the orientation of a leaf in 3D space
        and is returned as a unit vector [x, y, z].

        Parameters
        ----------
        distribution : str
            Leaf angle distribution type. Supported values:
            - "uniform" or "spherical": samples a random direction uniformly
            over the surface of the unit sphere.
            - "planophile": leaves are mostly horizontal, with the normal pointing
            upward along the z-axis ([0, 0, 1]).
            - "erectophile": leaves are mostly vertical, with the normal pointing
            along the x-axis ([1, 0, 0]).

        Returns
        -------
        np.ndarray
            A 3-element unit vector [x, y, z] representing the leaf normal.

        Raises
        ------
        ValueError
            If an unknown distribution type is provided.

        Notes
        -----
        - For "uniform"/"spherical", the returned vector is a random point on the
        unit sphere, representing a completely random leaf orientation.
        - For "planophile" and "erectophile", the returned vector is fixed along
        the principal axis (z or x) and not random.
        """
    if distribution in ("uniform", "spherical"):
        # Random direction on unit sphere
        phi = np.random.uniform(0, 2 * np.pi)
        cos_theta = np.random.uniform(-1, 1)
        sin_theta = np.sqrt(1 - cos_theta**2)
        return np.array([
            sin_theta * np.cos(phi),
            sin_theta * np.sin(phi),
            cos_theta
        ])

    elif distribution == "planophile":
        # Mostly horizontal leaves
        return np.array([0.0, 0.0, 1.0])

    elif distribution == "erectophile":
        # Mostly vertical leaves
        return np.array([1.0, 0.0, 0.0])

    else:
        raise ValueError("Unknown leaf angle distribution")





def sample_point_in_crown(
    shape: str,
    height: float,
    radius: float
) -> np.ndarray:
    """
    Sample a random point inside a tree crown volume of a specified shape.

    The function generates a 3D point [x, y, z] randomly distributed inside
    the crown volume. The crown shapes can be spherical, cylindrical, or conical.

    Parameters
    ----------
    shape : str
        Shape of the crown. Supported values:
        - "sphere": full spherical crown centered at the origin, scaled in the
          z-direction to match the specified height.
        - "sphere_w_LH": spherical crown without the lower hemisphere (upper half only),
          scaled in the z-direction to match the specified height.
        - "cylinder": cylindrical crown with constant radius in the xy-plane
          and height along the z-axis.
        - "cone": conical crown tapering linearly from the base radius to zero
          at the top along the z-axis.
    height : float
        Vertical extent of the crown along the z-axis. For spherical crowns,
        z-coordinates are scaled so that the total height equals this value.
    radius : float
        Maximum horizontal radius of the crown in the xy-plane.

    Returns
    -------
    np.ndarray
        A 3-element array [x, y, z] representing the coordinates of a point
        randomly sampled inside the crown volume.

    Raises
    ------
    ValueError
        If an unsupported crown shape is provided.

    Notes
    -----
    - For "sphere" and "sphere_w_LH", the point is sampled uniformly inside a
      unit sphere, then scaled to match the crown height.
    - For "sphere_w_LH", only the upper hemisphere (z ≥ 0) is used.
    - For "cylinder" and "cone", radial distance is sampled using sqrt(rand)
      to ensure uniform density across the cross-sectional area.
    - This function assumes the crown is centered at the origin and extends
      along the positive z-axis.
    """
    if shape == "sphere":
        while True:
            point = np.random.uniform(-radius, radius, size=3)
            if np.linalg.norm(point) <= radius:
                point[2] = point[2] * height / radius
                return point

    if shape == "sphere_w_LH":
        while True:
            point = np.random.uniform(-radius, radius, size=3)
            if np.linalg.norm(point) <= radius:
                point[2] = abs(point[2]) * height / radius
                return point

    elif shape == "cylinder":
        r = radius * np.sqrt(np.random.rand())
        theta = np.random.uniform(0, 2 * np.pi)
        z = np.random.uniform(0, height)
        return np.array([r * np.cos(theta), r * np.sin(theta), z])

    elif shape == "cone":
        z = np.random.uniform(0, height)
        r_max = radius * (1 - z / height)
        r = r_max * np.sqrt(np.random.rand())
        theta = np.random.uniform(0, 2 * np.pi)
        return np.array([r * np.cos(theta), r * np.sin(theta), z])

    else:
        raise ValueError("Unsupported crown shape")






def generate_tree(
    trunk_height: float,
    trunk_radius: float,
    crown_shape: str,
    crown_height: float,
    crown_radius: float,
    lai: float,
    leaf_radius: float,
    leaf_angle_distribution: str,
    position: List[float]
) -> Dict:
    """
    Generate a single 3D tree model with trunk and leaves.

    The function creates a trunk and distributes leaves within the crown
    volume. Leaf positions and orientations are sampled according to the
    crown shape and leaf angle distribution. The total number of leaves is
    derived from the leaf area index (LAI).

    Parameters
    ----------
    trunk_height : float
        Height of the tree trunk (same units as position and crown dimensions).
    trunk_radius : float
        Radius of the tree trunk.
    crown_shape : str
        Shape of the crown. Supported values: "sphere", "sphere_w_LH", "cylinder", "cone".
    crown_height : float
        Vertical extent of the crown from its base.
    crown_radius : float
        Maximum horizontal radius of the crown.
    lai : float
        Leaf area index, used to calculate the number of leaves as:
        n_leaves = (LAI * crown area) / leaf area.
    leaf_radius : float
        Radius of individual leaves.
    leaf_angle_distribution : str
        Leaf orientation distribution. Supported values:
        "uniform", "spherical", "planophile", "erectophile".
    position : List[float]
        [x, y, z] coordinates of the tree base in world space.

    Returns
    -------
    Dict
        A dictionary representing the tree with keys:
        - "trunk": dictionary with keys
            - "base": 3-element array of the trunk base position [x, y, z].
            - "height": trunk height.
            - "radius": trunk radius.
        - "leaves": list of dictionaries, each with keys
            - "center": 3-element array of leaf position [x, y, z].
            - "radius": leaf radius.
            - "normal": 3-element array representing leaf orientation.

    Notes
    -----
    - Leaf positions are sampled randomly inside the crown volume based on `crown_shape`.
    - Leaf normals are sampled according to `leaf_angle_distribution`.
    - Crown base is positioned at the top of the trunk.
    - Number of leaves is computed from LAI and crown/leaf areas.
    - All positions are returned in world coordinates relative to the tree base.
    """
    # Trunk
    trunk = {
        "base": np.array(position),
        "height": trunk_height,
        "radius": trunk_radius
    }

    # Crown base position
    crown_base_z = position[2] + trunk_height

    # Compute number of leaves from LAI
    crown_area = np.pi * crown_radius**2
    leaf_area = np.pi * leaf_radius**2
    n_leaves = int((lai * crown_area) / leaf_area)

    leaves = []

    for _ in range(n_leaves):
        local_pos = sample_point_in_crown(
            crown_shape, crown_height, crown_radius
        )
        world_pos = np.array([
            position[0] + local_pos[0],
            position[1] + local_pos[1],
            crown_base_z + local_pos[2]
        ])

        leaf = {
            "center": world_pos,
            "radius": leaf_radius,
            "normal": sample_leaf_normal(leaf_angle_distribution)
        }
        leaves.append(leaf)

    return {
        "trunk": trunk,
        "leaves": leaves
    }

