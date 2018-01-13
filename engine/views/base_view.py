
from engine.models.base_model import BaseModel

from pyglet.graphics import glTranslatef, glRotatef, glPushMatrix, glPopMatrix, GLfloat, glGetFloatv, \
    GL_MODELVIEW_MATRIX, glMultMatrixf, glLoadIdentity, glTranslated


class BaseView(object):

    def __init__(self, model: BaseModel, mesh=None):
        self._model = model
        self._sub_views = set()

        self._model_view_matrix = (GLfloat * 16)()
        self._model.observe(self.update)
        self.update()
        if mesh:
            self._mesh = mesh
        else:
            print("No mesh for {}".format(model.name))
            self._draw = self._draw_nothing

    def add_sub_view(self, sub_view):
        self._sub_views.add(sub_view)

    def update(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(*self._model.position)
        glRotatef(self._model.pitch, 1, 0, 0)
        glRotatef(self._model.yaw, 0, 1, 0)
        glRotatef(self._model.roll, 0, 0, 1)
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
        self._mesh.draw()

    def _draw_nothing(self):
        pass

    def tear_down_matrix(self):
        glPopMatrix()

    def align_camera(self):
        glRotatef(-self._model.yaw, 0, 1, 0)

    def center_camera(self):
        glRotatef(-self._model.pitch, 1, 0, 0)
        glRotatef(-self._model.yaw, 0, 1, 0)
        glRotatef(-self._model.roll, 0, 0, 1)
        x, y, z = self._model.position
        glTranslated(-x, -y - 23, -z)
