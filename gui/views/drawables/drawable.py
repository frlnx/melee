import pyglet

from engine.models.observable import Observable


class Drawable(Observable):
    __abstract__ = True

    SIGNAL_RECOLOR = 1
    SIGNAL_REPOSITION = 2
    SIGNAL_REPOSITION_TEXTURE = 3
    SIGNAL_RENORMALIZE = 4

    @property
    def n_coordinates(self):
        raise NotImplementedError()

    @property
    def draw_data(self):
        raise NotImplementedError()

    @property
    def vertex_mode(self):
        raise NotImplementedError()

    @property
    def vertices(self):
        raise NotImplementedError()

    @property
    def normals_mode(self):
        raise NotImplementedError()

    @property
    def normals(self):
        raise NotImplementedError()

    @property
    def color_mode(self):
        raise NotImplementedError()

    @property
    def colors(self):
        raise NotImplementedError()

    @property
    def tex_coord_mode(self):
        raise NotImplementedError()

    @property
    def tex_coords(self):
        raise NotImplementedError()

    @property
    def group(self) -> "pyglet.graphics.Group":
        raise NotImplementedError()

    @property
    def mode(self):
        raise NotImplementedError()
