
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
            self._draw = self._draw_nothing

    def set_model(self, model: BaseModel):
        self._model.unobserve(self.update)
        self._model = model
        self._model.observe(self.update)
        self.update()

    def set_mesh(self, mesh):
        self._mesh = mesh
        self._draw = self._draw_mesh

    def add_sub_view(self, sub_view):
        self._sub_views.add(sub_view)

    def update(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(*self.position)
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(self.roll, 0, 0, 1)
        glGetFloatv(GL_MODELVIEW_MATRIX, self._model_view_matrix)
        glPopMatrix()

    @property
    def position(self):
        return self._model.position

    @property
    def pitch(self):
        return self._model.pitch

    @property
    def yaw(self):
        return self._model.yaw

    @property
    def roll(self):
        return self._model.roll

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

    def _draw_mesh(self):
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

    def clear_sub_views(self):
        self._sub_views.clear()


class DummyView(BaseView):

    def __init__(self, *args, **kwargs):
        pass

    def set_model(self, model: BaseModel):
        pass

    def set_mesh(self, mesh):
        pass

    def add_sub_view(self, sub_view):
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def set_up_matrix(self):
        pass

    def draw_sub_views(self):
        pass

    def _draw(self):
        pass

    def _draw_mesh(self):
        pass

    def _draw_nothing(self):
        pass

    def tear_down_matrix(self):
        pass

    def align_camera(self):
        pass

    def center_camera(self):
        pass
