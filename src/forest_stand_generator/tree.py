# src/forest_stand_generator/tree.py

import numpy as np
from typing import Dict, List



import numpy as np

def sample_leaf_normal(distribution: str) -> np.ndarray:
    """
    Sample a leaf normal vector based on a specified leaf angle distribution.

    Parameters
    ----------
    distribution : str
        The leaf angle distribution type. Supported values are:
        - "uniform" or "spherical": random direction on the unit sphere.
        - "planophile": leaves mostly horizontal (z-axis).
        - "erectophile": leaves mostly vertical (x-axis).

    Returns
    -------
    np.ndarray
        A 3-element array representing the sampled leaf normal vector [x, y, z].

    Raises
    ------
    ValueError
        If an unknown distribution type is provided.
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
    Sample a random point inside a tree crown volume.

    Parameters
    ----------
    shape : str
        The shape of the crown. Supported values are:
        - "sphere": a full spherical crown centered at the origin,
        scaled in the z-direction to match the given height.
        - "sphere_w_LH": a spherical crown **without the lower hemisphere**
        (i.e., only the upper half of the sphere is used), scaled in the
        z-direction to match the given height.
        - "cylinder": a cylindrical crown with constant radius.
        - "cone": a conical crown tapering linearly to zero radius at the top.
    height : float
        The height of the crown (z-direction). For spherical crowns, the z-coordinates
        are scaled so the total vertical extent equals this height.
    radius : float
        The maximum radius of the crown in the xy-plane.

    Returns
    -------
    np.ndarray
        A 3-element array representing the coordinates [x, y, z] of a point
        randomly sampled inside the crown volume.

    Raises
    ------
    ValueError
        If an unsupported crown shape is provided.
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
    Generate a single tree model with trunk and leaves.

    Parameters
    ----------
    trunk_height : float
        Height of the tree trunk.
    trunk_radius : float
        Radius of the tree trunk.
    crown_shape : str
        Shape of the crown. Supported: "sphere", "cylinder", "cone".
    crown_height : float
        Height of the crown (vertical extent).
    crown_radius : float
        Maximum radius of the crown in the horizontal plane.
    lai : float
        Leaf area index. Determines the number of leaves as
        (LAI * crown area) / leaf area.
    leaf_radius : float
        Radius of individual leaves.
    leaf_angle_distribution : str
        Leaf angle distribution. Supported: "uniform", "spherical",
        "planophile", "erectophile".
    position : List[float]
        [x, y, z] coordinates of the tree base.

    Returns
    -------
    Dict
        A dictionary with two keys:
        - "trunk": dictionary containing trunk "base", "height", and "radius".
        - "leaves": list of dictionaries, each with "center" (position),
          "radius", and "normal" (leaf orientation vector).

    Notes
    -----
    - Leaf positions are randomly sampled within the crown volume based on
      `crown_shape`.
    - Leaf normals are sampled according to `leaf_angle_distribution`.
    - The total number of leaves is computed from LAI and leaf/crown areas.
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

