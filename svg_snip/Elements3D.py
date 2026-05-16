""" Generation of Scalable Vector Graphics in HTML snippets
-- WIP --
Created by A. Aichert on Sat Nov 25th 2023

# Example when also using ProjectiveGeometry32

from svg_snip.Composer import Composer
from svg_snip.Jupyter import CanvasWithOverlay
from ProjectiveGeometry23.homography import rotation_x, rotation_y, scale
from ProjectiveGeometry23.central_projection import ProjectionMatrix
from ProjectiveGeometry23.svg_utils import svg_world_geometry


vis = CanvasWithOverlay(400, 300)

cam = ProjectionMatrix.perspective_look_at([0,0,100], image_size=(vis.w, vis.h))

# World transformation
pitch, yaw = 0.0, 0.0   # pitch = vertical angle, yaw = horizontal angle
s = 0.2

def handle_draw(vis):
    global pitch, yaw
    if vis.mouse_state.clicked:
        dx, dy = vis.mouse_state.dx, vis.mouse_state.dy
        yaw += dx * 0.01        # horizontal drag → rotate around world Y
        pitch += dy * 0.01      # vertical drag → rotate around local X

        # Clamp pitch to avoid flipping
        pitch = max(-np.pi/2 + 0.1, min(np.pi/2 - 0.1, pitch))

    svg = Composer((vis.w, vis.h))
    svg.add(svg_world_geometry)

    # Build transformation:
    # First yaw (around world Y), then pitch (around rotated X axis)
    T = scale(s) @ rotation_x(pitch) @ rotation_y(yaw)

    raw_svg_code = svg.render(P=cam.P @ T)
    vis.html_overlay.value = raw_svg_code

vis.handle_draw = handle_draw
vis.display()

"""

import numpy as np

from .Composer import Composer
from .Elements import line as line2D
from .Elements import text as text2D
from .Elements import arrow as arrow2D
from .Elements import circle

"""
Some projective Geometry utility.
"""

def cvec(vector):
    """Column vector from 1D array or list of values."""
    vector = np.array(vector)
    if vector.ndim == 1:
        vector = vector.reshape(-1, 1)
    return vector

def normalize(v):
    return np.array(v) / np.linalg.norm(v)

def dehomogenize(vector):
    """"Divides column vector by last element and returns all but last element."""
    vector = cvec(vector)
    return vector[0:-1] / vector[-1]

def rgba2hex(r, g, b, a=0.5):
    """
    Convert RGB or RGBA values (0-1) to a hex string.
    """
    return f'#{max(0, min(255, int(round(r*255)))):02X}{max(0, min(255, int(round(g*255)))):02X}{max(0, min(255, int(round(b*255)))):02X}{max(0, min(255, int(round(a*255)))):02X}'

"""
Basic 3D Elements
"""

def text(P, X, content, **kwargs):
    x = P@cvec(X)
    return text2D(x=x[0][0]/x[2][0], y=x[1][0]/x[2][0], content=content, **kwargs)


"""
Basic 3D Elements
"""

def point(P, X, r=3, fill="purple", **kwargs):
    x = P@cvec(X)
    return circle(cx=x[0][0]/x[2][0], cy=x[1][0]/x[2][0],
                  r=r, fill=fill, **kwargs)


def line(P, X1, X2, stroke="green", **kwargs):
    x1 = P@cvec(X1)
    x2 = P@cvec(X2)
    return line2D(x1=x1[0][0]/x1[2][0], y1=x1[1][0]/x1[2][0],
                  x2=x2[0][0]/x2[2][0], y2=x2[1][0]/x2[2][0],
                  stroke=stroke, **kwargs)


def arrow(P, X1, X2, stroke="green", text=None, **kwargs):
    """
    Generate SVG code for a 3D arrow projected onto a 2D plane.

    Parameters:
    - P (numpy 3x4 matrix): Projection matrix.
    - X1 (array-like): The 3D coordinates of the arrow's starting point.
    - X2 (array-like): The 3D coordinates of the arrow's end point.
    - stroke (str): The color of the arrow line and markers.
    - text (str): Optional text label to display along the arrow.

    kwargs:
     - head (str): Shape of the end marker ('sharp', 'barb', 'circle', 'star', 'cross', or None).
     - tail (str): Shape of the start marker ('sharp', 'barb', 'circle', 'star', 'cross', or None).

    Returns:
    str: SVG code for the projected arrow.
    """
    x1 = P @ cvec(X1)
    x2 = P @ cvec(X2)

    return arrow2D(
        x1=x1[0][0] / x1[2][0],
        y1=x1[1][0] / x1[2][0],
        x2=x2[0][0] / x2[2][0],
        y2=x2[1][0] / x2[2][0],
        stroke=stroke,
        text=text,
        **kwargs
    )

def wire_polygon(P, Xs, fill="none", stroke="black", **kwargs):
    xs = [dehomogenize(P@cvec(X)) for X in Xs]
    xs = ' '.join([f'{round(x[0][0],2)},{round(x[1][0],2)}' for x in xs])
    return f'<polygon points="{xs}" fill="{fill}" stroke="{stroke}" />'


def polygon(P, Xs, fill="#00ff4080", stroke="black", stroke_back="#00000080", **kwargs):
    """
    Draw a 3D polygon from 4D homogeneous points.
    """
    xs = [dehomogenize(P @ cvec(X)) for X in Xs]
    front_facing = (xs[1][0]-xs[0][0])*(xs[2][1]-xs[0][1]) - (xs[1][1]-xs[0][1])*(xs[2][0]-xs[0][0]) > 0
    xs = ' '.join([f'{round(x[0][0],2)},{round(x[1][0],2)}' for x in xs])
    style_attr = f'stroke="{stroke}" fill="{fill}"' if front_facing else f'stroke="{stroke_back}" fill="none"'
    return f'<polygon points="{xs}" {style_attr} />'


def polygon_with_lighting(P, Xs, fill="#00ff4080", stroke="none", **kwargs):
    """
    Draw a 3D polygon with simple Lambertian lighting applied as a brightness filter.
    """
    # Convert points to 3D euclidean vectors
    pts = [dehomogenize(X).flatten() for X in Xs]  # first 3 points for normal
    normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
    light_dir = P[2, 0:3].flatten() / np.linalg.norm(P[2, 0:3])
    b = 0.5 + 0.5 * np.abs(np.dot(light_dir, normal / np.linalg.norm(normal)))
    if np.isnan(b):
        b = 0
    # fill = rgba2hex(b,b,b)

    # Project all points to 2D for SVG
    xs = [dehomogenize(P @ X).flatten() for X in Xs]
    front_facing = (xs[1][0]-xs[0][0])*(xs[2][1]-xs[0][1]) - (xs[1][1]-xs[0][1])*(xs[2][0]-xs[0][0]) > 0
    if not front_facing:
        return ""

    xs_str = ' '.join([f'{round(x[0],2)},{round(x[1],2)}' for x in xs])
    style_attr = f'fill="{fill}"'
    if stroke is not None and stroke != "none":
        style_attr += f' stroke="{stroke}"'
    style_attr += f' style="filter:brightness({max(0, min(100, int(b*100))) }%)"'

    return f'<polygon points="{xs_str}" {style_attr} />'

"""
Basic 3D Shapes
"""

def wire_cube(P, min, max, stroke="blue", **kwargs):
    v = [
        np.array([min[0],min[1],min[2],1]).reshape(-1, 1),
        np.array([max[0],min[1],min[2],1]).reshape(-1, 1),
        np.array([min[0],max[1],min[2],1]).reshape(-1, 1),
        np.array([max[0],max[1],min[2],1]).reshape(-1, 1),
        np.array([min[0],min[1],max[2],1]).reshape(-1, 1),
        np.array([max[0],min[1],max[2],1]).reshape(-1, 1),
        np.array([min[0],max[1],max[2],1]).reshape(-1, 1),
        np.array([max[0],max[1],max[2],1]).reshape(-1, 1)
    ]
    el = ['<g>']
    for a in range(8):
        for b in range(8):
            m1 = a%2 != b%2
            m2 = (a//2)%2 != (b//2)%2
            m3 = (a//4)%2 != (b//4)%2
            if (m1+m2+m3) == 1:
                el = el + [line(P, v[a], v[b], stroke=stroke, **kwargs)]
    
    return '\n  '.join(el) + '\n</g>\n'


def cube(P, min, max, fill="#00ff4080", **kwargs):
    """
    Draw a cube (or cuboid) as filled polygons with front-face fill and back-face wireframe.

    Parameters:
        P: projection matrix (3x4)
        min: 3D coordinates of the minimum corner (x0, y0, z0)
        max: 3D coordinates of the maximum corner (x1, y1, z1)
        stroke: outline color
        fill: fill color for front faces
    """
    # 8 cube corners in homogeneous coords
    corners = [
        np.array([min[0], min[1], min[2], 1.0]),  # 0
        np.array([max[0], min[1], min[2], 1.0]),  # 1
        np.array([min[0], max[1], min[2], 1.0]),  # 2
        np.array([min[0], min[1], max[2], 1.0]),  # 3
        np.array([max[0], max[1], min[2], 1.0]),  # 4
        np.array([max[0], min[1], max[2], 1.0]),  # 5
        np.array([min[0], max[1], max[2], 1.0]),  # 6
        np.array([max[0], max[1], max[2], 1.0]),  # 7
    ]

    faces = [
        [0, 1, 4, 2],  # bottom
        [0, 3, 5, 1],  # front
        [0, 2, 6, 3],  # left
        [7, 6, 2, 4],  # back
        [7, 5, 3, 6],  # right
        [7, 4, 1, 5],  # top
    ]
    
    svg_elements = ["<g>"]
    for face in faces:
        face_points = [corners[i] for i in face]  # homogeneous 4D points
        svg_elements.append("  " + polygon_with_lighting(P, face_points, fill=fill, **kwargs))
    svg_elements.append("</g>")
    return "\n".join(svg_elements)

    
def sphere(P, center=(0,0,0,1), radius=50.0, subdivisions=True, fill="#00ff4080", **kwargs):
    """Render a geodesic sphere as SVG polygons with optional lighting."""
    center = dehomogenize(center).flatten()
    t = (1+np.sqrt(5))/2
    verts = [normalize(v) for v in [
        [-1,t,0],[1,t,0],[-1,-t,0],[1,-t,0],
        [0,-1,t],[0,1,t],[0,-1,-t],[0,1,-t],
        [t,0,-1],[t,0,1],[-t,0,-1],[-t,0,1]
    ]]
    faces = [
        [0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],
        [1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],
        [3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],
        [4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]
    ]
    for s in range(1 if subdivisions else 0): # more subdivs possible but very expensive!
        new_faces=[]
        for f in faces:
            a=normalize((verts[f[0]]+verts[f[1]])/2)
            b=normalize((verts[f[1]]+verts[f[2]])/2)
            c=normalize((verts[f[2]]+verts[f[0]])/2)
            verts.extend([a,b,c])
            i=len(verts)-3
            new_faces+=[[f[0],i,i+2],[i,f[1],i+1],[i+2,i+1,f[2]],[i,i+1,i+2]]
        faces=new_faces
    # scale and translate vertices
    verts=[np.append(np.array(v)*radius+np.array(center),1.0) for v in verts]
    # render SVG
    svg=["<g>"]
    for f in faces:
        svg.append("  "+polygon_with_lighting(P,[verts[i] for i in f], fill=fill, **kwargs))
    svg.append("</g>")
    return "\n".join(svg)


def volume(P, shape, model_matrix=np.eye(4), color_axes=True, lighting=True, **kwargs):
    """
    Visualize a 3D volume as a cube oriented in space.
    Optionally color the three edges from origin to +x/+y/+z in red, green and blue respectively.
    
    Parameters:
        P: projection matrix
        shape: tuple/list of 3 ints (Z, Y, X)
        model_matrix: 4x4 matrix mapping voxel coordinates to world coordinates
        color_axes: adds extra colored lines for origin to x/y/z corner points.
        lighting: if True, uses polygon_with_lighting else just polygon

    For additional kwargs see polygon_with_lighting(...) or polygon(...) respectively.
    """
    # Cube corners in voxel coordinates (homogeneous)
    X, Y, Z = shape[2], shape[1], shape[0]
    corners_voxel = [
        np.array([0, 0, 0, 1]),
        np.array([X, 0, 0, 1]),
        np.array([0, Y, 0, 1]),
        np.array([0, 0, Z, 1]),
        np.array([X, Y, 0, 1]),
        np.array([X, 0, Z, 1]),
        np.array([0, Y, Z, 1]),
        np.array([X, Y, Z, 1])
    ]

    # Transform corners with model_matrix
    corners = [model_matrix @ c for c in corners_voxel]

    # Define cube faces (each face as list of corner indices)
    faces = [
        [0, 1, 4, 2],  # bottom
        [0, 3, 5, 1],  # front
        [0, 2, 6, 3],  # left
        [7, 6, 2, 4],  # back
        [7, 5, 3, 6],  # right
        [7, 4, 1, 5],  # top
    ]

    # Render faces with lighting
    svg = ["<g>"]
    for f in faces:
        if lighting:
            svg.append("  " + polygon_with_lighting(P, [corners[i] for i in f], **kwargs))
        else:
            svg.append("  " + polygon(P, [corners[i] for i in f], **kwargs))

    # Optional colored axes from origin
    if color_axes:
        origin = corners[0]
        axes_ends = [corners[1], corners[2], corners[3]]  # +X, +Y, +Z
        colors = ["red", "green", "blue"]
        for end, color in zip(axes_ends, colors):
            line_kwargs = kwargs.copy()
            line_kwargs.pop("stroke", None)  # remove stroke from kwargs if present
            svg.append(line(P, origin, end, stroke=color, **line_kwargs))

    svg.append("</g>")
    return "\n".join(svg)
