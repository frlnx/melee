from ctypes import c_float

from pyglet.gl import GL_TRIANGLES, GL_QUADS, glInterleavedArrays, glDrawArrays


class DrawBundle:
    shape_by_n_points = {3: GL_TRIANGLES, 4: GL_QUADS}

    def __init__(self, draw_shape, n_dimensions, vertices: list=None, normals: list=None, tex_coords: list=None,
                 colors: list=None):
        self._n_dimensions = n_dimensions
        self._draw_shape = draw_shape
        self._n_vertices = len(vertices)
        self.draw_data = []
        self._vertices = vertices
        self._normals = normals
        self._tex_coords = tex_coords
        self._colors = colors
        self._draw_data_encoding_mode = self._determine_data_encoding_mode()
        self.data_length = len(self.draw_data)
        self.c_arr = c_float * self.data_length
        self.c_draw_data = self.c_arr(*self.draw_data)

    def _determine_data_encoding_mode(self):
        return 'v3f'

    def draw(self):
        glInterleavedArrays(self._draw_data_encoding_mode, 0, self.c_draw_data)
        glDrawArrays(self._draw_shape, 0, self._n_vertices)
