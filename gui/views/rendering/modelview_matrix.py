from typing import Callable

from pyglet.gl import *

from engine.physics.force import MutableVector


class ModelViewMatrix:
    _to_cfloat_sixteen_array: Callable = GLfloat * 16

    def __init__(self, position: MutableVector=None, rotation: MutableVector=None, scale: MutableVector=None):
        self._position = position
        self._rotation = rotation
        self._scale = scale
        self._model_view_matrix = self._to_cfloat_sixteen_array()
        self._dimensional_update_functions = []
        if self._position:
            self._position.observe(self.update_model_matrix, "move")
            self._dimensional_update_functions.append(self._translate)
        if self._rotation:
            self._rotation.observe(self.update_model_matrix, "move")
            self._dimensional_update_functions.append(self._rotate)
        if self._scale:
            self._scale.observe(self.update_model_matrix, "move")
            self._dimensional_update_functions.append(self._scaling)
        self.update_model_matrix()

    def update_model_matrix(self):
        glPushMatrix()
        glLoadIdentity()
        for dimension_update_function in self._dimensional_update_functions:
            dimension_update_function()
        glGetFloatv(GL_MODELVIEW_MATRIX, self._model_view_matrix)
        glPopMatrix()

    def _translate(self):
        glTranslatef(*self._position)

    def _rotate(self):
        glRotatef(self._rotation.x, 1, 0, 0)
        glRotatef(self._rotation.y, 0, 1, 0)
        glRotatef(self._rotation.z, 0, 0, 1)

    def _scaling(self):
        glScalef(*self._scale)
