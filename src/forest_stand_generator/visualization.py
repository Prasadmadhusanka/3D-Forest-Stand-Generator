import numpy as np
import plotly.graph_objects as go
from .data_validation import validate_plot


def plot_forest_stand(stand, plot_width=20, plot_length=20, resolution=20):
    """
    Plot 3D forest stand with fixed plot boundaries

    Args:
        stand: List of tree dictionaries
        plot_width: Width of the plot (y-axis dimension)
        plot_length: Length of the plot (x-axis dimension)
        resolution: Resolution for cylinder/leaf meshes
    """
    validate_plot(plot_width, plot_length)

    fig = go.Figure()

    # Cylinder for trunk (solid)
    def create_cylinder_mesh(x, y, z_base, height, radius, resolution=20):
        theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
        circle_x = radius * np.cos(theta) + x
        circle_y = radius * np.sin(theta) + y
        z_bottom = np.full(resolution, z_base)
        z_top = np.full(resolution, z_base + height)

        # Combine bottom and top vertices + centers
        vertices_x = np.concatenate([circle_x, circle_x, [x, x]])
        vertices_y = np.concatenate([circle_y, circle_y, [y, y]])
        vertices_z = np.concatenate([z_bottom, z_top, [z_base, z_base + height]])

        i, j, k = [], [], []

        # side faces
        for t in range(resolution):
            b0 = t
            b1 = (t + 1) % resolution
            t0 = t + resolution
            t1 = (t + 1) % resolution + resolution
            i.append(b0)
            j.append(b1)
            k.append(t1)
            i.append(b0)
            j.append(t1)
            k.append(t0)

        # bottom cap
        center_bottom = 2 * resolution
        for t in range(resolution):
            i.append(center_bottom)
            j.append(t)
            k.append((t + 1) % resolution)

        # top cap
        center_top = 2 * resolution + 1
        for t in range(resolution):
            i.append(center_top)
            j.append(t + resolution)
            k.append((t + 1) % resolution + resolution)

        return vertices_x, vertices_y, vertices_z, i, j, k

    # Disk for leaf (filled)
    def create_filled_leaf(center, radius, normal, resolution=20):
        """
        Returns x, y, z, i, j, k for a filled disk oriented by normal
        """
        # circle in XY plane
        theta = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
        circle = np.stack(
            [radius * np.cos(theta), radius * np.sin(theta), np.zeros_like(theta)],
            axis=1,
        )

        # rotation to align z-axis to normal
        normal = np.array(normal) / np.linalg.norm(normal)
        z_axis = np.array([0, 0, 1])
        if np.allclose(normal, z_axis):
            R = np.eye(3)
        elif np.allclose(normal, -z_axis):
            R = np.diag([1, 1, -1])
        else:
            v = np.cross(z_axis, normal)
            s = np.linalg.norm(v)
            c = np.dot(z_axis, normal)
            vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
            R = np.eye(3) + vx + vx @ vx * ((1 - c) / (s**2))

        # rotate and translate
        circle = (R @ circle.T).T + np.array(center)
        center_point = np.array(center)

        # vertices
        X = np.vstack([center_point, circle])[:, 0]
        Y = np.vstack([center_point, circle])[:, 1]
        Z = np.vstack([center_point, circle])[:, 2]

        # triangle fan
        i, j, k = [], [], []
        for t in range(1, resolution):
            i.append(0)
            j.append(t)
            k.append(t + 1)
        # close the fan
        i.append(0)
        j.append(resolution)
        k.append(1)

        return X, Y, Z, i, j, k

    # Plot trunks
    for tree in stand:
        trunk = tree["trunk"]
        x0, y0, z0 = trunk["base"]
        h = trunk["height"]
        r = trunk["radius"]

        X, Y, Z, i, j, k = create_cylinder_mesh(x0, y0, z0, h, r, resolution)
        fig.add_trace(
            go.Mesh3d(x=X, y=Y, z=Z, i=i, j=j, k=k, color="saddlebrown", opacity=1.0)
        )

    # Plot leaves
    for tree in stand:
        for leaf in tree["leaves"]:
            X, Y, Z, i, j, k = create_filled_leaf(
                leaf["center"], leaf["radius"], leaf["normal"], resolution
            )
            fig.add_trace(
                go.Mesh3d(x=X, y=Y, z=Z, i=i, j=j, k=k, color="green", opacity=0.7)
            )

    fig.update_layout(
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            xaxis=dict(range=[0, plot_length]),
            yaxis=dict(range=[0, plot_width]),
            aspectmode="manual",
            aspectratio=dict(x=plot_length, y=plot_width, z=plot_length),
        )
    )

    fig.show()


def plot_forest_top_view(stand, plot_width=20, plot_length=20):
    """
    Plot 2D top view of forest stand with fixed plot boundaries

    Args:
        stand: List of tree dictionaries
        plot_width: Width of the plot (y-axis dimension)
        plot_length: Length of the plot (x-axis dimension)
    """
    validate_plot(plot_width, plot_length)

    fig = go.Figure()

    # Plot trunk footprints (circles)
    for tree in stand:
        trunk = tree["trunk"]
        x0, y0, _ = trunk["base"]
        r = trunk["radius"]

        theta = np.linspace(0, 2 * np.pi, 50)
        x = x0 + r * np.cos(theta)
        y = y0 + r * np.sin(theta)

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                fill="toself",
                mode="lines",
                line=dict(color="saddlebrown"),
                fillcolor="saddlebrown",
            )
        )

    # Plot leaf projections (ellipses)
    for tree in stand:
        for leaf in tree["leaves"]:
            x0, y0, _ = leaf["center"]
            r = leaf["radius"]

            # normalize normal vector
            n = np.array(leaf["normal"], dtype=float)
            n /= np.linalg.norm(n)

            # z-aligned leaves → circle
            nz = abs(n[2])
            if nz < 1e-4:
                continue  # edge-on leaf, no visible area

            # ellipse axes
            a = r  # major axis
            b = r * nz  # minor axis

            # orientation of ellipse
            angle = np.arctan2(n[1], n[0])

            t = np.linspace(0, 2 * np.pi, 40)
            ct, st = np.cos(t), np.sin(t)

            # rotated ellipse
            x = x0 + a * ct * np.cos(angle) - b * st * np.sin(angle)
            y = y0 + a * ct * np.sin(angle) + b * st * np.cos(angle)

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    fill="toself",
                    mode="lines",
                    line=dict(color="green"),
                    fillcolor="green",
                    opacity=0.5,
                )
            )

    # Layout
    fig.update_layout(
        title="Forest Top View (2D Projection)",
        xaxis_title="X (Length)",
        yaxis_title="Y (Width)",
        showlegend=False,
        xaxis=dict(range=[0, plot_length], constrain="domain"),
        yaxis=dict(
            range=[0, plot_width], scaleanchor="x", scaleratio=1, constrain="domain"
        ),
        # Add a rectangle to show plot boundaries
        shapes=[
            dict(
                type="rect",
                xref="x",
                yref="y",
                x0=0,
                y0=0,
                x1=plot_length,
                y1=plot_width,
                line=dict(color="Black", width=2),
                fillcolor="rgba(0,0,0,0)",
                layer="below",
            )
        ],
    )

    fig.show()
