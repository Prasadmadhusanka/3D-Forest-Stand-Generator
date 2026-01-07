# src/forest_stand_generator/visualization.py

import plotly.graph_objects as go

def plot_forest_stand_plotly(stand):
    fig = go.Figure()

    # Plot trunks as lines
    for tree in stand:
        trunk = tree['trunk']
        x0, y0, z0 = trunk['base']
        h = trunk['height']
        fig.add_trace(go.Scatter3d(
            x=[x0, x0], y=[y0, y0], z=[z0, z0+h],
            mode='lines', line=dict(color='brown', width=5)
        ))

    # Plot leaves as points
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