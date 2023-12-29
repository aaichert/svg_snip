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

from IPython.display import display, HTML
import html


def indent(text):
    lines = text.split('\n')
    indented_lines = ['  ' + line for line in lines]
    indented_text = '\n'.join(indented_lines)
    return indented_text


class Composer:
    """
    A class for generating SVG images with customizable parametrized shapes.

    Attributes:
        image_size (tuple): Tuple (width, height) defining the SVG size.
        scene (list): List of tuples containing shape functions and kwargs.
    Static member:
        declared_shapes (dict): Dictionary of shape definitions by fn name.
                                Used e.g. for def's and named g's.
        
    Declaration of Shapes:
        A shape consists of a definition and a function returning a string.
        The definition is added to the beginning of the <svg> only if the
        function has been added to the scene and no more than once.
        A shape is decleared when a module is loaded and its definition and
        function (name) added to declared_shapes.
    """
    
    declared_shapes = dict()
    
    def __init__(self, image_size):
        """
        Initialize the Composer object.

        Args:
            image_size (tuple): Tuple of (width, height) defining the SVG image size.
        """
        self.image_size = image_size
        self.scene = []

    @classmethod
    def declare(cls, func, definitions):
        """
        Declare a custom shape definition.

        Args:
            func (function): Shape function to associate with the definition.
            definitions (dict): SVG definition string by unique id of the tag.
        """
        cls.declared_shapes[func.__name__] = definitions

    def add(self, func, **kwargs):
        """
        Add a shape to the scene.

        Args:
            func (function): Shape function to add to the scene.
            **kwargs: Keyword arguments for the shape function.
            
        Returns:
            kwargs (mutable) as they are represented in the scene.

        Example:
            from svg_snip.E
            svg = Composer([200,200])
            svg_snip.add(circle, cx=100, cy=100)
            svg_snip.display()
        """
        self.scene.append((func, kwargs))
        return self.scene[-1]

    def render(self, debug=False, nested=False, extra_defs=None, **override_kwargs):
        """
        Generate the SVG code for the image.

        Args:
            nested (bool): Is this a nested (recursive) call to render?
            extra_defs (dict): accumulates definitions from nested calls.
            **override_kwargs (dict): arguments to override scene kwargs.

        Returns either:
        (nested == False):
            str: complete SVG code for the image, including outer <svg ...>
                 tag with size information and a <defs> section.            
        (nested == True):
            Tupel (str, dict) of partial svg code and extra_defs for parent
                              call to render(...)
        """
        svg = []
        
        functions_used = {func_kwargs[0].__name__ for func_kwargs in self.scene}
        declarations_used = [self.declared_shapes[fn_name] for fn_name in functions_used if fn_name in self.declared_shapes]
        definitions = extra_defs or dict()
        for dictionary_of_defs in declarations_used:
            definitions.update(dictionary_of_defs)

        if len(definitions) > 0 and extra_defs != True:
            svg.append('<defs>')
            for tagid in definitions:
                svg.append(indent(definitions[tagid]))
            svg.append('</defs>')
        
        for func, kwargs in self.scene:
            merged_kwargs = {**kwargs, **override_kwargs}
            merged_kwargs['composer'] = self
            svg.append(func(**merged_kwargs))
        
        raw_html = f'<svg width="{self.image_size[0]}" height="{self.image_size[1]}" viewBox="0 0 {self.image_size[0]} {self.image_size[1]}" xmlns="http://www.w3.org/2000/svg">\n' + '\n'.join([indent(s) for s in svg]) + '\n</svg>'
        
        if debug:
            return f'<details close><summary>show html</summary><pre>{html.escape(raw_html, quote=True)}</pre></details>\n{raw_html}'
        else:
            return raw_html

    def update(self, **override_kwargs):
        if not hasattr(self, 'widget'):
            raise RuntimeError("You must call display() before update.")
        widget.value = self.render(**override_kwargs)

    def display(self, debug=False, **override_kwargs):
        """
        Display the rendered SVG image in a Jupyter Notebook.
        This function is mostly for testing. See also: CanvasWithOverlay in Jupyter.py
        """
        self.widget = HTML(self.render(debug=debug, **override_kwargs))
        display(self.widget)


