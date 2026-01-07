# src/forest_stand_generator/export.py

def export_forest_stand_to_csv(stand: list, filename: str):
    """
    Export tree positions and leaves to CSV for external use.

    CSV columns:
    tree_id, type, x, y, z, radius, nx, ny, nz

    type = "trunk" or "leaf"
    nx, ny, nz = leaf normal (0 for trunk)
    """
    import csv

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['tree_id', 'type', 'x', 'y', 'z', 'radius', 'nx', 'ny', 'nz'])

        for tid, tree in enumerate(stand):
            trunk = tree['trunk']
            x0, y0, z0 = trunk['base']
            h = trunk['height']
            r = trunk['radius']
            # Trunk (approximate as base point)
            writer.writerow([tid, 'trunk', x0, y0, z0, r, 0, 0, 0])
            # Leaves
            for leaf in tree['leaves']:
                lx, ly, lz = leaf['center']
                nr, ng, nb = leaf['normal']
                writer.writerow([tid, 'leaf', lx, ly, lz, leaf['radius'], nr, ng, nb])