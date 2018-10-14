from pyglet.gl import GL_LINES

from .drawable import Drawable


class Box(Drawable):
    
    def __init__(self, left, right, bottom, top, color: tuple):
        super().__init__()
        self._verticies = [
            left, bottom, right, bottom,
            right, bottom, right, top,
            right, top, left, top,
            left, top, left, bottom
        ]
        self._colors = color * 8
        self._draw_data = [(self.vertex_mode, self.vertices), (self.color_mode, self.colors)]

    def set_color(self, color: tuple):
        self._colors = color * 8
        self._draw_data = [(self.vertex_mode, self.vertices), (self.color_mode, self.colors)]
        self._callback(self.SIGNAL_RECOLOR)

    def update_boundaries(self, left, right, bottom, top):
        self._verticies[:] = (
            left, bottom, right, bottom,
            right, bottom, right, top,
            right, top, left, top,
            left, top, left, bottom
        )
        self._callback(self.SIGNAL_REPOSITION)

    @property
    def n_coordinates(self):
        return 8

    @property
    def group(self):
        return None

    @property
    def normals(self):
        return []

    @property
    def mode(self):
        return GL_LINES

    @property
    def draw_data(self):
        return self._draw_data

    @property
    def vertex_mode(self):
        return 'v2f'

    @property
    def vertices(self):
        return self._verticies

    @property
    def color_mode(self):
        return 'c3f'

    @property
    def colors(self):
        return self._colors
