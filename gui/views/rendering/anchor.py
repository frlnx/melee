from pyglet.gl import *


class Anchor:
    cost = 16

    def __init__(self, model_view_matrix):
        self._model_view_matrix = model_view_matrix

    def __enter__(self):
        glPushMatrix()
        glMultMatrixf(self._model_view_matrix)

    def __exit__(self, exc_type, exc_val, exc_tb):
        glPopMatrix()
