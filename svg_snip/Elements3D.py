""" Generation of Scalable Vector Graphics in HTML snippets
-- WIP --
Created by A. Aichert on Sat Nov 25th 2023
"""

import numpy as np

from .Composer import Composer
from .Elements import line as line2D
from .Elements import text as text2D
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

def dehomogenize(vector):
    """"Divides all elemnts in an iterable by last element.
    returns all but last element."""
    return [c/vector[-1] for c in vector[0:-1]]


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


def polygon(P, Xs, fill="#00ff40", stroke="green", **kwargs):
    xs = [dehomogenize(P@cvec(X)) for X in Xs]
    xs = ' '.join([f'{x[0][0]},{x[1][0]}' for x in xs])
    return f'<polygon points="{xs}" fill="{fill}" stroke="{stroke}" />'


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


def wire_pyramid(P, C, XO, XU, XV, XUV, stroke="#00000080", **kwargs):
    el = [
        '<g>',
        # base
        line(P, XO, XU),
        line(P, XO, XV),
        line(P, XU, XUV),
        line(P, XV, XUV),
        # tip
        line(P, C, XO),
        line(P, C, XU),
        line(P, C, XV),
        line(P, C, XUV),        
    ]    
    return '\n  '.join(el) + '\n</g>\n'



