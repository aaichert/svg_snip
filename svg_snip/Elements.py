""" Generation of Scalable Vector Graphics in HTML snippets
-- WIP --
Created by A. Aichert on Sat Aug 19th 2023

Usage:
    from svg_snip.Composer import Composer
    from svg_snip.Elements import circle
    svg = Composer([200,200])
    svg.add(circle, cx=100, cy=100)
    print(svg.render())
    
Usage (in Jupyterlab):
    from svg_snip.Composer import Composer
    from svg_snip.Elements import circle
    svg = Composer([200,200])
    svg.add(circle, cx=100, cy=100)
    svg.display()

See also: CanvasWithOverlay in Jupyter.py
"""

"""
Generic generation of functions to create basic svg snippets (rect, line...)
"""

from .Composer import Composer


def attributes(args_attributes, **kwargs):
    """ Build a string of SVG attributes.
    Start description with "(float)" to round values to two digits."""
    svg_code = ''
    for arg_name, arg_desc in args_attributes.items():
        svg_arg_name = arg_name.replace('_', '-')  # Convert snake_case to kebab-case
        if arg_name == 'content':
            continue  # Special case: <element arg1="value1" ...>content</element>
        if arg_name in kwargs:
            if arg_desc.startswith('(float)'):
                svg_code += f'{svg_arg_name}="{kwargs[arg_name]:.2f}" '
            else:
                svg_code += f'{svg_arg_name}="{kwargs[arg_name]}" '
    return svg_code


def define_svg_element(element_attributes):
    """
    Define an SVG element function based on the given description.

    Parameters:
    element_attributes (dict): A dictionary describing the SVG element.

    Returns:
    function: The generated SVG element function.
    """
    def svg_element(**kwargs):
        svg_code = f'<{element_attributes["name"]} '
        svg_code += attributes(element_attributes["args"], **kwargs)
        if 'content' in kwargs:
            svg_code += f'>{kwargs["content"]}</{element_attributes["name"]}>'
        else:
            svg_code += '/>'
        return svg_code

    # Add docstring to the generated function
    indent_line = "\n    "
    svg_element.__doc__ = f"""
    Generate SVG code for the <{element_attributes["name"]}> element.

    Parameters:
    {indent_line.join([f"- {arg}: {desc}" for arg, desc in element_attributes["args"].items()])}

    Returns:
    {element_attributes["return"]}
    """

    return svg_element


"""
Basic Shapes
"""


# All basic SVG elements will have this.
default_attributes = {
    "style": "(str): Inline style attribute for setting multiple CSS properties at once.",
    "transform": "(str): Specifies a transformation such as "
}


# All basic SVG elements that have an outline will have all of this.
stroke_attributes = {
    "stroke": "(str): The stroke color of the outline. Examples: 'currentColor' keyword, 'red', #FF0000, rgb(255,0,0) ...",
    "stroke_width": "(float): The width of the outline.",
    "stroke_opacity": "(float): The opacity of the outline. A value between 0 (transparent) and 1 (opaque).",
    "stroke_dasharray": "(str): Defines the pattern of dashes and gaps used in the outline.",
    "stroke_linecap": "(str): Specifies the shape to be used at the end of the outline. Possible values are 'butt', 'round', and 'square'.",
    "stroke_linejoin": "(str): Specifies the shape to be used at the corners of the outline. Possible values are 'miter', 'round', and 'bevel'.",
    "stroke_miterlimit": "(float): Sets the limit for the length of the miter on joined corners of the outline.",
    "marker_start": "(str): Specifies the marker symbol for the start of the line.",
    "marker_mid": "(str): Specifies the marker symbol for the middle of the line.",
    "marker_end": "(str): Specifies the marker symbol for the end of the line."
}


fill_attributes = {
    "fill": "(str): The fill color. Examples: 'currentColor' keyword, 'red', #FF0000, rgb(255,0,0) ...",
    "fill_opacity": "(float): The opacity of the shape's fill. A value between 0 (completely transparent) and 1 (completely opaque).",
    "fill_rule": "(str): Defines the inside of the shape to dertermine the fill region. Possible values are 'nonzero' and 'evenodd'.",
    "pattern": "(str): URL referencing a <pattern> element to be used as the fill.",
    "gradient": "(str): URL referencing a <linearGradient> or <radialGradient> element to be used as the fill."
}


font_attributes = {
    "font_size": "(float): The font size of the text.",
    "font_family": "(str): The font family for the text.",
    "font_variant": "(str): Controls the usage of alternate glyphs for the text. Possible values are 'normal' or 'small-caps'.",
    "text_decoration": "(str): Specifies decorations added to the text. Possible values are 'none', 'underline', 'overline', and 'line-through'.",
    "text_transform": "(str): Controls the capitalization of the text. Possible values are 'none', 'capitalize', 'uppercase', and 'lowercase'.",
    "word_spacing": "(float/str): The spacing between words. Can be a numeric value or a string with units (e.g., '2', '2em').",
    "letter_spacing": "(float/str): The spacing between characters. Can be a numeric value or a string with units (e.g., '1', '1em').",
    "direction": "(str): Specifies the text direction. Possible values are 'ltr' (left-to-right) and 'rtl' (right-to-left).",
    "text_anchor": "(str): The alignment of the text. Possible values are 'start', 'middle', and 'end'.",
    "writing_mode": "(str): The writing mode for the text. Possible values are 'lr-tb' (default), 'rl-tb', 'tb-rl', 'lr' (vertical text), 'rl' (vertical text), 'tb' (horizontal text).",
    "dominant_baseline": "(str): Examples: 'baseline', 'middle', 'central', 'ideographic', 'alphabetic', 'hanging', 'mathematical'...",
    "unicode_bidi": "(str): Set bidirectional algorithm: 'normal', 'embed', 'bidi-override', 'isolate', and 'isolate-override'."
}


# SVG Rectangle description
rect_attributes = {
    "name": "rect",
    "args": {
        "x": "(float): The x-coordinate of the top-left corner of the rectangle.",
        "y": "(float): The y-coordinate of the top-left corner of the rectangle.",
        "width": "(float): The width of the rectangle.",
        "height": "(float): The height of the rectangle.",
        "rx": "(float): The horizontal radius of the rectangle's corners for rounded corners.",
        "ry": "(float): The vertical radius of the rectangle's corners for rounded corners.",
        "fill": "(str): The fill color of the rectangle. Accepts any valid SVG color.",
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <rect> element with the specified attributes."
}
rect = define_svg_element(rect_attributes)


# SVG Circle description
circle_attributes = {
    "name": "circle",
    "args": {
        "cx": "(float): The x-coordinate of the center of the circle.",
        "cy": "(float): The y-coordinate of the center of the circle.",
        "r": "(float): The radius of the circle.",
        **fill_attributes,
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <circle> element with the specified attributes."
}
circle = define_svg_element(circle_attributes)


# SVG Ellipse description
ellipse_attributes = {
    "name": "ellipse",
    "args": {
        "cx": "(float): The x-coordinate of the center of the ellipse.",
        "cy": "(float): The y-coordinate of the center of the ellipse.",
        "rx": "(float): The horizontal radius of the ellipse.",
        "ry": "(float): The vertical radius of the ellipse.",
        **fill_attributes,
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <ellipse> element with the specified attributes."
}
ellipse = define_svg_element(ellipse_attributes)


# SVG Line description
line_attributes = {
    "name": "line",
    "args": {
        "x1": "(float): The x-coordinate of the start point of the line.",
        "y1": "(float): The y-coordinate of the start point of the line.",
        "x2": "(float): The x-coordinate of the end point of the line.",
        "y2": "(float): The y-coordinate of the end point of the line.",
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <line> element with the specified attributes."
}
line = define_svg_element(line_attributes)


# Text description
text_attributes = {
    "name": "text",
    "args": {
        "x": "(float): The x-coordinate of the starting point of the text baseline.",
        "y": "(float): The y-coordinate of the starting point of the text baseline.",
        "content": "(str): The text content to be displayed.",
        **font_attributes,
        **fill_attributes,
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <text> element with the specified attributes."
}
text = define_svg_element(text_attributes)


# SVG Path description
path_attributes = {
    "name": "path",
    "args": {
        "d": "(str): A string representing the path data. It consists of commands and parameters to define the path.",
        "fill": "(str): The fill color of the path. Accepts any valid SVG color.",
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <path> element with the specified attributes."
}
path = define_svg_element(path_attributes)


# SVG Polygon description
polygon_attributes = {
    "name": "polygon",
    "args": {
        "points": "(str): A space-separated list of x, y coordinate pairs defining the vertices of the polygon.",
        **fill_attributes,
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <polygon> element with the specified attributes."
}
polygon = define_svg_element(polygon_attributes)


# SVG Polyline description
polyline_attributes = {
    "name": "polyline",
    "args": {
        "points": "(str): A space-separated list of x, y coordinate pairs defining the vertices of the polyline.",
        **fill_attributes,
        **stroke_attributes,
        **default_attributes
    },
    "return": "str: SVG code for the <polyline> element with the specified attributes."
}
polyline = define_svg_element(polyline_attributes)


"""
Advanced Example (including definition) Shapes
"""

def cross(x=0, y=0, size=4, stroke='', **kwargs):
    """
    Generate SVG code for a cross.

    Args:
        x, y: position
        size: size of the cross.
    """
    if stroke != '':
        stroke =  f'style="stroke: {stroke};"'
    return f'<use {stroke} xlink:href="#cross" transform="translate({x:.2f},{y:.2f}) scale({size / 6:.2f})"/>'

Composer.declare(cross, {'cross': """<g id="cross">
  <line x1="-5" y1="-5" x2="5" y2="5" stroke-width="2"/>
  <line x1="-5" y1="5" x2="5" y2="-5" stroke-width="2"/>
</g>"""})

def star(x=0, y=0, size=4, fill='', **kwargs):
    """
    Generate SVG code for a star.

    Args:
        x, y: position
        size: size of the star.
    """
    if fill != '':
        fill = f'style="fill: {fill};"'
    return f'<use {fill} xlink:href="#star" transform="translate({x:.2f},{y:.2f}) scale({size / 10:.2f})"/>'

Composer.declare(star, {'star': """<g id="star">
  <polygon points="0,-10 2.76,-3.5 9.51,-3.5 4.63,1.5 7.39,8 0,4.5 -7.39,8 -4.63,1.5 -9.51,-3.5 -2.76,-3.5" stroke-width="2"/>
</g>"""})

def heart(x=0, y=0, size=4, angle=0, fill='', **kwargs):
    """
    Generate SVG code for a heart.

    Args:
        x, y: position
        size: size of the heart.
    """
    if fill != '' :
        fill = f'style="fill: {fill};"'
    return f'<use {fill} xlink:href="#heart" transform="translate({x:.2f},{y:.2f}) scale({size / 10:.2f}) rotate({angle})"/>'

Composer.declare(heart, {'heart': """<g id="heart">
<path d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314z"/>
</g>"""})

def arrow(start_x, start_y, end_x, end_y, arrow_length=10, arrow_width=6, **kwargs):
    """
    Generate SVG code for an arrow. TODO use marker instead.

    Parameters:
    - start_x (float): The x-coordinate of the arrow's starting point.
    - start_y (float): The y-coordinate of the arrow's starting point.
    - end_x (float): The x-coordinate of the arrow's end point.
    - end_y (float): The y-coordinate of the arrow's end point.
    - arrow_length (float): The length of the arrowhead.
    - arrow_width (float): The width of the arrowhead.

    kwargs:
     - stroke, stroke_width, and others, see also: line, polygon

    Returns:
    str: SVG code for the arrow.
    """
    # Generate SVG code for the line
    line_svg = line(start_x=start_x, start_y=start_y, end_x=end_x, end_y=end_y, **kwargs)

    # Calculate arrowhead points
    dx = end_x - start_x
    dy = end_y - start_y
    length = (dx**2 + dy**2)**0.5
    dx /= length
    dy /= length

    # Calculate arrowhead points
    arrowhead_x1 = end_x - arrow_length * dx - arrow_width * dy
    arrowhead_y1 = end_y - arrow_length * dy + arrow_width * dx
    arrowhead_x2 = end_x - arrow_length * dx + arrow_width * dy
    arrowhead_y2 = end_y - arrow_length * dy - arrow_width * dx

    # Generate SVG code for the polygon (arrowhead)
    polygon_svg = polygon(points=f"{end_x:.2f},{end_y:.2f} {arrowhead_x1:.2f},{arrowhead_y1:.2f} {arrowhead_x2:.2f},{arrowhead_y2:.2f}",
                               **kwargs)

    # Combine both SVG codes
    svg_code = line_svg + polygon_svg

    return svg_code
