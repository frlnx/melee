
from engine.models.base_model import BaseModel

from pyglet.graphics import glTranslatef, glRotatef, glPushMatrix, glPopMatrix, GLfloat, glGetFloatv, \
    GL_MODELVIEW_MATRIX, glMultMatrixf, glLoadIdentity


class BaseView(object):

    def __init__(self, model: BaseModel, sub_views: set):
        self._model = model
        self._sub_views = sub_views

        self._model_view_matrix = (GLfloat * 16)()
        self._model.observe(self.update)
        self.update()

    def update(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(*self._model.position)
        glRotatef(self._model.pitch, 1, 0, 0)
        glRotatef(self._model.yaw, 0, 1, 0)
        glRotatef(self._model.bank, 0, 0, 1)
        glGetFloatv(GL_MODELVIEW_MATRIX, self._model_view_matrix)
        glPopMatrix()

    def draw(self):
        self.set_up_matrix()
        self.draw_sub_views()
        self._draw()
        self.tear_down_matrix()

    def set_up_matrix(self):
        glPushMatrix()
        glMultMatrixf(self._model_view_matrix)

    def draw_sub_views(self):
        for subview in self._sub_views:
            subview.draw()

    def _draw(self):
        pass

    def tear_down_matrix(self):
        glPopMatrix()
