# src/forest_stand_generator/export.py

import json
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """
    JSON encoder that enables serialization of NumPy data types.

    This encoder converts NumPy arrays into Python lists so they
    can be written to standard JSON files.
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def export_forest_stand_to_json(stand: list, filename: str):
    """
    Export a forest stand to a JSON file.

    The file is written to the current working directory unless
    a path is explicitly included in the filename.

    Parameters
    ----------
    stand : list
        Forest stand data structure.
        Each element represents a tree and contains:
            - trunk: base position, height, radius
            - leaves: list of leaf objects with center, radius, and normal
    filename : str
        Name of the output JSON file (e.g. "forest_stand.json").

    Notes
    -----
    NumPy arrays inside the stand structure are automatically
    converted to standard Python lists.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            stand,
            f,
            indent=4,
            cls=NumpyEncoder
        )


def export_forest_stand_to_csv(stand: list, filename: str):
    """
    Export forest stand geometry to a CSV file.

    Each row represents either a trunk or a leaf.

    CSV Columns
    -----------
    tree_id : int
        Index of the tree in the forest stand.
    type : str
        Either "trunk" or "leaf".
    x, y, z : float
        Spatial coordinates.
        - Trunk: base position
        - Leaf: center position
    radius : float
        Radius of the trunk or leaf.
    nx, ny, nz : float
        Normal vector of the leaf.
        Set to (0, 0, 0) for trunks.

    Parameters
    ----------
    stand : list
        Forest stand data structure.
    filename : str
        Name of the output CSV file (e.g. "forest_stand.csv").

    Notes
    -----
    Trunks are exported as a single point located at the trunk base.
    Leaf geometry is represented by its center, radius, and normal.
    """
    import csv

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'tree_id', 'type', 'x', 'y', 'z',
            'radius', 'nx', 'ny', 'nz'
        ])

        for tid, tree in enumerate(stand):
            trunk = tree['trunk']
            x0, y0, z0 = trunk['base']
            r = trunk['radius']

            # Trunk (exported as base point)
            writer.writerow([tid, 'trunk', x0, y0, z0, r, 0, 0, 0])

            # Leaves
            for leaf in tree['leaves']:
                lx, ly, lz = leaf['center']
                nx, ny, nz = leaf['normal']
                writer.writerow([
                    tid, 'leaf', lx, ly, lz,
                    leaf['radius'], nx, ny, nz
                ])
