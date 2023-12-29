""" CanvasWithOverlay
-- WIP --
Created by A. Aichert on Sat Aug 19th 2023

Usage (in Jupyterlab):
    from svg_snip.Jupyter import CanvasWithOverlay
    
    vis = CanvasWithOverlay(200,200)
    
    def handle_draw(vis):
        x,y = vis.mouse_state.pos()
        vis.canvas[1].clear()
        vis.canvas[1].fill_style = "red" if vis.mouse_state.clicked else "blue"
        vis.canvas[1].fill_rect(x-2,y-2,5,5)
        if vis.mouse_state.clicked:
            vis.canvas[0].fill_style = "#00000011"
            vis.canvas[0].fill_rect(x-2,y-2,5,5)
    vis.handle_draw = handle_draw
    
    vis.display()



Example with vector overlay:
    
Usage (in Jupyterlab):
    from svg_snip.Jupyter import CanvasWithOverlay
    from svg_snip.Composer import Composer
    from svg_snip.Elements import heart
    
    vis = CanvasWithOverlay(200,200)
    
    def handle_draw(vis):
        x,y = vis.mouse_state.pos()
        svg = Composer((vis.w, vis.h))
        svg.add(heart, x=x, y=y, size=8,
            fill="red" if vis.mouse_state.clicked else "blue")
        vis.html_overlay.value = svg.render()
        if vis.mouse_state.clicked:
            vis.canvas[0].fill_style = "#00000011"
            vis.canvas[0].fill_rect(x-2,y-2,5,5)
        
    vis.handle_draw = handle_draw
    
    vis.display()
"""

from dataclasses import dataclass
from IPython.display import display
import ipywidgets as widgets
from ipywidgets import Output, HTML

from ipycanvas import MultiCanvas, hold_canvas


@dataclass
class MouseState:
    x: int = 0
    y: int = 0
    dx: int = 0
    dy: int = 0
    clicked: bool = False
    def update(self, nx, ny):
        self.dx, self.dy = nx - self.x, ny - self.y
        self.x, self.y = nx, ny
    def pos(self):
        return self.x, self.y
    

class CanvasWithOverlay():
    """ A Canvas for iPythonWidgets with two layers (background and an overlay
    as pixel graphics) with and additional optional SVG overlay.
    """
    def __init__(self, width, height, handle_draw=None, background="#D0D0D0FF"):
        self.w, self.h = width, height
        self.mouse_state = MouseState()
        
        self.out = Output()

        self.handle_key = None  # handle_key(key: str)
        self.handle_mouse = None  # handle_mouse(mouse: MouseState)
        self.handle_draw = handle_draw  # handle_draw(vis: CanvasWithOverlay)

        self.canvas = MultiCanvas(2, width=width, height=height)
        self.canvas.layout.width = f'{width}px'
        self.canvas.layout.height = f'{height}px'
        
        self.canvas.add_class("dimension")
        with hold_canvas():
            self.canvas.global_alpha = 0.5
            self.canvas[0].fill_style = background
            self.canvas[0].fill_rect(0,0,width,height)
            self.canvas[0].fill_style = "#00000055"
            self.canvas[1].clear()

        # Create an HTML widget with the provided SVG content and 'overlay' class
        svg_content = '''
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <!-- add vector graphics here, see also Python class svg_snip.Composer-->
</svg>
'''
        self.html_overlay = widgets.HTML(value=svg_content)
        self.html_overlay.add_class("dimension")
        self.html_overlay.add_class("overlay")

        # Combine the widgets in a container with the 'container' class
        self.container = widgets.HBox([self.canvas, self.html_overlay])
        self.container.add_class("dimension")
        self.container.add_class("container")

        # Custom CSS styles
        self.custom_css = """
<style>
  .dimension {
    top: 0;
    left: 0;
    width: """ + str(width) + """px;
    height: """ + str(height) + """px;
    margin:0;
    padding:0;
  }

  .container {
    overflow: hidden;
    position: relative;
  }

  .overlay {
    position: absolute;
    pointer-events: none;
  }
</style>
"""

        for event in ["mouse_move", "mouse_down", "mouse_up", "mouse_out", "key_down"]:
            getattr(self.canvas, 'on_' + event)(getattr(self, 'internal_' + event))

        self.widget = widgets.VBox([HTML(self.custom_css), self.container, self.out])


    def internal_mouse_move(self, x, y):
        self.mouse_state.update(x,y)
        if self.handle_mouse:
            self.handle_mouse(self.mouse_state)
        self.redraw()
        
    def internal_mouse_down(self, x, y):
        self.mouse_state = MouseState(x, y, clicked=True)
        self.internal_mouse_move(x,y)
    
    def internal_mouse_up(self, x, y):
        self.mouse_state = MouseState(x, y, clicked=False)
        self.internal_mouse_move(x,y)

    def internal_mouse_out(self, x, y):
        self.mouse_state = MouseState(x, y, clicked=False)
        self.internal_mouse_move(x,y)

    def internal_key_down(self, key, shift_key, ctrl_key, meta_key):
        if (key and key!=""):
            self.handle_key(key)
        self.redraw()

    def redraw(self):
        if self.handle_draw:
            with hold_canvas():
                with self.out:
                    self.handle_draw(self)
            
    def display(self):
        display(self.widget)
        self.redraw()

