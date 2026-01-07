import numpy as np
import plotly.graph_objects as go

def plot_forest_stand_plotly(stand, resolution=20):
    fig = go.Figure()

    def create_cylinder_mesh(x, y, z_base, height, radius, resolution=20):
        """
        Returns x, y, z, i, j, k for go.Mesh3d
        """
        # Generate circle points
        theta = np.linspace(0, 2*np.pi, resolution, endpoint=False)
        circle_x = radius * np.cos(theta) + x
        circle_y = radius * np.sin(theta) + y
        z_bottom = np.full(resolution, z_base)
        z_top = np.full(resolution, z_base + height)

        # Combine bottom and top vertices
        vertices_x = np.concatenate([circle_x, circle_x])
        vertices_y = np.concatenate([circle_y, circle_y])
        vertices_z = np.concatenate([z_bottom, z_top])

        # Create side faces (quads split into triangles)
        i, j, k = [], [], []
        for t in range(resolution):
            b0 = t
            b1 = (t + 1) % resolution
            t0 = t + resolution
            t1 = (t + 1) % resolution + resolution

            # first triangle of quad
            i.append(b0); j.append(b1); k.append(t1)
            # second triangle of quad
            i.append(b0); j.append(t1); k.append(t0)

        return vertices_x, vertices_y, vertices_z, i, j, k

    # Plot trunks
    for tree in stand:
        trunk = tree['trunk']
        x0, y0, z0 = trunk['base']
        h = trunk['height']
        r = trunk['radius']

        X, Y, Z, i, j, k = create_cylinder_mesh(x0, y0, z0, h, r, resolution)
        fig.add_trace(go.Mesh3d(
            x=X, y=Y, z=Z,
            i=i, j=j, k=k,
            color='saddlebrown',
            opacity=1.0
        ))

    # Plot leaves
    leaf_x, leaf_y, leaf_z = [], [], []
    for tree in stand:
        for leaf in tree['leaves']:
            lx, ly, lz = leaf['center']
            leaf_x.append(lx)
            leaf_y.append(ly)
            leaf_z.append(lz)

    fig.add_trace(go.Scatter3d(
        x=leaf_x, y=leaf_y, z=leaf_z,
        mode='markers',
        marker=dict(size=3, color='green')
    ))

    fig.update_layout(scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Z'
    ))
    fig.show()
