"""
Generation of Scalable Vector Graphics (SVG) as HTML snippets

See also:
    Elements for all basic SVG shapes and some advanced functions
    Elements3D for creating 3D svg overlays (no depth buffer)
               based on a single 3x4 projective matrix called "P".

-- WIP --
Created by A. Aichert on Sat Aug 19th 2023

Usage:
    from svg_snip.Composer import Composer
    from svg_snip.Elements import circle, line
    
    svg = Composer([200, 200])
    svg.add(circle, cx=100, cy=100, r=5)

    # Supports groups:
    group = Group()
    group.add(line, x1=50, y1=150, x2=150, y2=50, stroke="yellow", stroke_width=4)
    svg.add(group, transform="translate(10,10)")
    
    print(svg.render())

Usage in JupyterLab:
    from svg_snip.Composer import Composer
    from svg_snip.Elements import circle

    svg = Composer([200, 200])
    svg.add(circle, cx=100, cy=100, r=5)
    svg.display()

See also: CanvasWithOverlay in Jupyter.py
"""

import io
import html
import base64
from typing import Optional, Callable
from IPython.display import display, HTML

from PIL import Image

ShapeFunc = Callable[..., str]


def indent(text: str, n: int = 2) -> str:
    lines = text.split('\n')
    indented_lines = [' ' * n + line for line in lines]
    return '\n'.join(indented_lines)

def image(data, x=0, y=0, width=None, height=None, sparse=0, **kwargs) -> str:
    """
    Generate SVG code for a base-64 encoded image

    Args:
        data: PIL image or base64 encoded image as ascii
        x, y: position
        width, height: (optional) size
        sparse: number of colors for PNG compression if >0
    """
    if isinstance(data, Image.Image):
        buffered = io.BytesIO()
        if sparse is not None and sparse > 0:
            if sparse > 1:
                data = data.convert("P", palette=Image.ADAPTIVE, colors=sparse)
            data.save(buffered, format="PNG", optimize=True)
        else:
            data.save(buffered, format="JPEG")
        data = base64.b64encode(buffered.getvalue()).decode()

    attributes = ""
    if height is not None:
        attributes += f'height="{height:.2f}px" '
    if width is not None:
        attributes += f'width="{width:.2f}px" '

    return f'<image x="{x:.2f}px" y="{y:.2f}px" {attributes} href="data:image/png;charset=utf-8;base64,{data}" />'


class Group:
    """
    Container for SVG elements grouped inside a <g> element with proper indentation.

    Attributes:
        children (list[tuple[ShapeFunc, dict]]): List of shape functions and their parameters.

    Args:
        children (list[tuple[ShapeFunc, dict]], optional): Initial children to add to the group.
        kwargs (dict[str, str], optional): Default attributes for the <g> element (e.g., transform, style).

    Usage example:
        group = Group(
            children=[(circle, {'cx': 50, 'cy': 50, 'r': 20, 'fill': 'red'})],
            transform="translate(10, 20)"
        )
        group.add(line, x1=0, y1=0, x2=100, y2=100, stroke='black')
        print(group())
    """

    declared_shapes: dict[str, dict[str, str]] = {}

    VALID_GROUP_ATTRIBUTES = {
        "id", "class", "style", "display", "tabindex", "transform",
        "pointer-events", "visibility", "opacity", "filter", "mask", "clip-path", "cursor",
        "fill", "fill-opacity", "stroke", "stroke-width", "stroke-opacity",
        "font-family", "font-size", "font-weight",
        "onclick", "onmouseover", "onmouseout", "onmousedown", "onmouseup", "onmouseenter", "onmouseleave"
    }

    def __init__(self, 
                 children: list[tuple[ShapeFunc, dict]] | None = None, 
                 **kwargs: str) -> None:
        self.children: list[tuple[ShapeFunc, dict]] = children if children is not None else []
        # Filter only valid group attributes from kwargs
        self.kwargs = {k: v for k, v in kwargs.items() if k in self.VALID_GROUP_ATTRIBUTES}

    def add(self, func: ShapeFunc, **kwargs) -> tuple[ShapeFunc, dict]:
        self.children.append((func, kwargs))
        return self.children[-1]

    def __call__(self, *, composer: Optional["Composer"] = None, **call_kwargs) -> str:
        # Merge stored kwargs with call_kwargs; call_kwargs override
        merged_attribs = {**self.kwargs, **{k: v for k, v in call_kwargs.items() if k in self.VALID_GROUP_ATTRIBUTES}}
        attribs_str = ' '.join(f'{k}="{v}"' for k, v in merged_attribs.items())

        content = []
        for func, child_kwargs in self.children:
            merged_kwargs = {**child_kwargs, **call_kwargs}
            if composer is not None:
                merged_kwargs['composer'] = composer
            content.append(func(**merged_kwargs))

        childrens_svg_code = "\n".join(content)
        return f'<g {attribs_str}>\n{indent(childrens_svg_code)}' + '\n</g>'

    @classmethod
    def declare(cls, func: ShapeFunc, definitions: dict[str, str]) -> None:
        cls.declared_shapes[func.__name__] = definitions


class Composer(Group):
    """
    Composer for generating scalable vector graphics (SVG) as HTML snippets.

    Inherits from Group and serves as the main container for SVG elements
    with support for adding shapes, grouping, rendering SVG markup, and
    displaying inline in Jupyter environments.

    Attributes:
        image_size (tuple[int, int]): Dimensions of the SVG canvas or background image.
        scale (float): Scaling factor for the SVG output size (default is 1).
        widget (IPython.display.HTML or None): Holds the displayed SVG widget in Jupyter.

    Args:
        canvas (tuple[int, int] | PIL.Image.Image | None): Defines canvas size or background image.
            If a PIL Image is provided, it is embedded as a background image in the SVG.
            If a tuple, sets the width and height of the SVG canvas.
            Defaults to (100, 100) if None.
        sparse (int | None): Optional color reduction for embedded PNG images (applies when canvas is an Image).

    Methods:
        render(debug=False, nested=False, extra_defs=None, extra_attrib='', **override_kwargs) -> str:
            Renders the full SVG markup as a string, optionally including debug info and extra definitions.
        update(**override_kwargs) -> None:
            Updates the displayed SVG widget in Jupyter with new rendering.
        display(debug=False, **override_kwargs) -> None:
            Displays the SVG inline in Jupyter, creating a new widget if needed.

    Usage example:
        from svg_snip.Composer import Composer
        from svg_snip.Elements import circle

        svg = Composer((200, 200))
        svg.add(circle, cx=100, cy=100, r=5)
        svg.display()
    """

    def __init__(self, canvas: None | tuple[int, int] | Image.Image = None, sparse: int | None = None) -> None:
        super().__init__()
        if isinstance(canvas, Image.Image):
            self.image_size = (canvas.width, canvas.height)
            # Add the background image shape automatically
            self.add(image, data=canvas, sparse=sparse)
        elif isinstance(canvas, tuple):
            self.image_size = canvas
        else:
            self.image_size = (100, 100)
        self.scale = 1
        self.widget: HTML | None = None

    def render(self, debug: bool = False, nested: bool = False, extra_defs: dict[str, str] | None = None, extra_attrib: str = '', **override_kwargs) -> str | tuple[str, dict[str, str]]:
        """
        Render the SVG content as a complete SVG markup string.
        
        This method generates the SVG markup by assembling all added shapes and groups,
        optionally including extra SVG definitions and attributes. It supports debugging
        output to show escaped HTML source and can return additional SVG definitions.
        
        Args:
            debug (bool, optional): If True, wraps the SVG output in a collapsible
                HTML details block showing the escaped SVG source code for debugging.
                Defaults to False.
            nested (bool, optional): Reserved for future use or nested rendering contexts.
                Defaults to False.
            extra_defs (dict[str, str] | None, optional): Additional SVG definitions
                (e.g., `<defs>` content) to include in the output. If True, skips wrapping
                in `<defs>`. Defaults to None.
            extra_attrib (str, optional): Extra attributes to add to the root `<svg>` element,
                e.g. `'class="my-svg" aria-hidden="true"'`. Defaults to an empty string.
            **override_kwargs: Arbitrary keyword arguments to override or add to
                shape function parameters during rendering.
        
        Returns:
            str: The full SVG markup as a string if debug is False.
            tuple[str, dict[str, str]]: A tuple of the SVG markup and the collected
                definitions dictionary if debug is True and extra_defs is True.
        
        Example:
            svg = Composer((200, 200))
            svg.add(circle, cx=100, cy=100, r=10)
            print(svg.render(debug=True, extra_attrib='class="icon"'))
        """
        functions_used = {func.__name__ for func, _ in self.children}
        definitions = extra_defs or {}
        for fn_name in functions_used:
            defs = self.declared_shapes.get(fn_name)
            if defs:
                definitions.update(defs)

        svg_parts = []
        if definitions and extra_defs is not True:
            svg_parts.append('<defs>')
            for defstr in definitions.values():
                svg_parts.append(indent(defstr))
            svg_parts.append('</defs>')

        for func, kwargs in self.children:
            merged_kwargs = {**kwargs, **override_kwargs, 'composer': self}
            svg_parts.append(func(**merged_kwargs))

        s = getattr(self, 'scale', 1)
        w, h = self.image_size
        raw_html = (
            f'<svg {extra_attrib} width="{w*s}" height="{h*s}" '
            f'viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">\n'
            + '\n'.join(indent(part) for part in svg_parts)
            + '\n</svg>'
        )

        if debug:
            return f'<details close><summary>show html</summary><pre>{html.escape(raw_html, quote=True)}</pre></details>\n{raw_html}'
        else:
            return raw_html

    def update(self, **override_kwargs) -> None:
        if self.widget is None:
            raise RuntimeError("You must call display() before update.")
        self.widget.value = self.render(**override_kwargs)

    def display(self, debug: bool = False, **override_kwargs) -> None:
        """
        Display the SVG inline in Jupyter by rendering the SVG markup via `render()`.
    
        Args:
            debug (bool, optional): Enable debug mode in rendering. Defaults to False.
            **override_kwargs: Additional arguments passed to `render()`.
    
        Raises:
            RuntimeError: If display is called in a non-Jupyter environment.
        """
        self.widget = HTML(self.render(debug=debug, **override_kwargs))
        display(self.widget)
