import ctypes

from pyglet.gl import GL_LIGHTING, GL_LIGHT0, GL_AMBIENT, \
    GL_DIFFUSE, GL_MODELVIEW_MATRIX
from pyglet.gl import glDisable, glLoadIdentity, glRotatef, glTranslatef, glScalef, \
    glPopMatrix, glPushMatrix, glEnable, glLightfv, glMultMatrixf, glTranslated, GLfloat, glGetFloatv

from engine.models.base_model import BaseModel


class BaseView(object):
    _to_cfloat_array = ctypes.c_float * 4
    _to_cfloat_three_array = ctypes.c_float * 3

    def __init__(self, model: BaseModel, mesh=None):
        self._model = model
        self._sub_views = set()
        self._mesh_scale = self.to_cfloat_array(1., 1., 1.)
        self._diffuse = self.to_cfloat_array(3., 3., 3., 1.)
        self._base_diffuse = (3., 3., 3., 1.)
        self._light_direction = self.to_cfloat_array(0, 0.3, 1, 0)
        self._ambience = self.to_cfloat_array(0.1, 0.1, 0.1, 0.1)
        self._base_ambience = (0.1, 0.1, 0.1, 0.1)
        self._model_view_matrix = (GLfloat * 16)()
        self._model.observe(self.update)
        self.update()
        if mesh:
            self._mesh = mesh
            self._draw = self._draw_mesh
        else:
            self._draw = self._draw_nothing
        self.yaw_catchup = 0

    def to_cfloat_array(self, *floats):
        if len(floats) == 3:
            return self._to_cfloat_three_array(*floats)
        return self._to_cfloat_array(*floats)

    def set_diffuse_multipliers(self, *rgba):
        self._diffuse = self.to_cfloat_array(*(x * y for x, y in zip(rgba, self._base_diffuse)))

    def set_ambience_multipliers(self, *rgba):
        self._ambience = self.to_cfloat_array(*(x * y for x, y in zip(rgba, self._base_ambience)))

    @property
    def is_alive(self):
        return self._model.is_alive

    def set_mesh_scale(self, scale):
        self._mesh_scale = self.to_cfloat_array(scale, scale, scale)
        self.update()

    def set_model(self, model: BaseModel):
        self._model.unobserve(self.update)
        self._model = model
        self._model.observe(self.update)
        self.update()

    def set_mesh(self, mesh):
        self._mesh = mesh
        if mesh:
            self._draw = self._draw_mesh
        else:
            self._draw = self._draw_nothing

    def add_sub_view(self, sub_view):
        self._sub_views.add(sub_view)

    def update(self):
        glPushMatrix()
        glLoadIdentity()
        glTranslatef(*self.position)
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(self.roll, 0, 0, 1)
        glScalef(*self._mesh_scale)
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
        self._light_on()
        self._draw()
        self._light_off()
        self._draw_local()
        self.tear_down_matrix()
        self._draw_global()

    def _draw_local(self):
        pass

    def _draw_global(self):
        pass

    def _light_on(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self._ambience)
        #lLightfv(GL_LIGHT0, GL_POSITION, self._light_direction)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self._diffuse)

    @staticmethod
    def _light_off():
        glDisable(GL_LIGHTING)

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
        yaw = -self._model.yaw #- (self._model.spin.yaw / 2 - self.yaw_catchup)
        glRotatef(yaw, 0, 1, 0)

    def center_camera(self):
        glRotatef(-self._model.pitch, 1, 0, 0)
        glRotatef(-self._model.yaw, 0, 1, 0)
        glRotatef(-self._model.roll, 0, 0, 1)
        x, y, z = self._model.position
        glTranslated(-x, -y - 23, -z)

    def clear_sub_views(self):
        self._sub_views.clear()

    def update_view_timer(self, dt):
        self.yaw_catchup += (self._model.spin.yaw - self.yaw_catchup) * dt * 2
