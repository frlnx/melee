import ctypes
from itertools import chain
from typing import Tuple, Callable

from pyglet.clock import schedule, schedule_once, unschedule
from pyglet.gl import GL_LIGHTING, GL_LIGHT0, GL_AMBIENT, \
    GL_DIFFUSE, GL_MODELVIEW_MATRIX
from pyglet.gl import glDisable, glLoadIdentity, glRotatef, glTranslatef, glScalef, \
    glPopMatrix, glPushMatrix, glEnable, glLightfv, glMultMatrixf, glTranslated, GLfloat, glGetFloatv
from pyglet.graphics import draw, GL_LINES

from engine.models.base_model import PositionalModel
from .opengl_animations import Explosion
from .opengl_drawables import ExplosionDrawable


class BaseView(object):
    # noinspection PyTypeChecker
    _to_cfloat_array: Callable = ctypes.c_float * 4
    # noinspection PyTypeChecker
    _to_cfloat_three_array: Callable = ctypes.c_float * 3
    # noinspection PyTypeChecker
    _to_cfloat_sixteen_array: Callable = GLfloat * 16

    def __init__(self, model: PositionalModel, mesh=None):
        self._model = model
        self._mesh_scale = self.to_cfloat_array(1., 1., 1.)
        self._diffuse = self.to_cfloat_array(3., 3., 3., 1.)
        self._base_diffuse = (3., 3., 3., 1.)
        self._light_direction = self.to_cfloat_array(0, 0.3, 1, 0)
        self._ambience = self.to_cfloat_array(0.1, 0.1, 0.1, 0.1)
        self._base_ambience = (0.1, 0.1, 0.1, 0.1)
        self._model_view_matrix = self._to_cfloat_sixteen_array()
        self._model.observe(self.update, "move")
        self._model.observe(self.explode, "explode")
        self._model.observe(self.alive_callback, "alive")
        self.update()
        self._mesh = mesh
        if mesh:
            self._draw = self._draw_mesh
            self._draw_transparent = self._draw_transparent_mesh
        else:
            self._draw = self._draw_nothing
            self._draw_transparent = self._draw_nothing
        self.yaw_catchup = 0
        if model.is_exploding:
            self.explode()

    def distance_to(self, other):
        return (self.position - other.position).distance

    @property
    def model(self):
        return self._model

    def explode(self):
        explosion = ExplosionDrawable()
        schedule(explosion.timer)
        schedule_once(lambda x: unschedule(explosion.timer), 2.)
        schedule_once(lambda x: self._mesh.remove_drawable(explosion), 2.)
        explosion_animator = Explosion(self._mesh.all_faces)
        self._mesh.add_animation(explosion_animator.animate)
        schedule_once(lambda x: explosion_animator.expire(), 6.)
        self._mesh.add_drawable(explosion)
        self._mesh.set_double_sided(True)

    def alive_callback(self):
        if self._model.is_alive:
            if self._mesh:
                self._draw = self._draw_mesh
        else:
            self._draw = self._draw_nothing

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

    def set_model(self, model: PositionalModel):
        self._model.unobserve(self.update, "move")
        self._model = model
        self._model.observe(self.update, "move")
        self.update()

    def set_mesh(self, mesh):
        self._mesh = mesh
        if mesh:
            self._draw = self._draw_mesh
            self._draw_transparent = self._draw_transparent_mesh
        else:
            self._draw = self._draw_nothing
            self._draw_transparent = self._draw_nothing

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
        self._light_on()
        self._draw()
        self._light_off()
        self._draw_local()
        self.tear_down_matrix()
        self._draw_global()

    def draw_transparent(self):
        self.set_up_matrix()
        self._light_on()
        self._draw_transparent()
        self._light_off()
        self._draw_local()
        self.tear_down_matrix()
        self._draw_global()

    @staticmethod
    def _draw_bbox(bbox, color: Tuple[int, int, int, int]=None):
        color = color or (255, 255, 255, 255)
        lines = bbox.lines
        v3f = [(line.x1, -10.0, line.y1, line.x2, -10.0, line.y2) for line in lines]
        v3f = list(chain(*v3f))
        n_points = int(len(v3f) / 3)
        v3f = ('v3f', v3f)
        c4b = ('c4B', color * n_points)
        draw(n_points, GL_LINES, v3f, c4b)

    @staticmethod
    def _draw_quadrant(x, y, color: Tuple[int, int, int, int]=None):
        color = color or (255, 255, 255, 255)
        v3f = [x * 30, -11, y * 30,
               (x + 1) * 30, -11, y * 30,
               (x + 1) * 30, -11, y * 30,
               (x + 1) * 30, -11, (y + 1) * 30,
               (x + 1) * 30, -11, (y + 1) * 30,
               x * 30, -11, (y + 1) * 30,
               x * 30, -11, (y + 1) * 30,
               x * 30, -11, y * 30]
        n_points = int(len(v3f) / 3)
        v3f = ('v3f', v3f)
        c4b = ('c4B', color * n_points)
        draw(n_points, GL_LINES, v3f, c4b)

    def _draw_local(self):
        pass

    def _draw_global(self):
        pass

    def _light_on(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self._ambience)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self._diffuse)

    @staticmethod
    def _light_off():
        glDisable(GL_LIGHTING)

    def set_up_matrix(self):
        glPushMatrix()
        glMultMatrixf(self._model_view_matrix)

    def _draw(self):
        self._mesh.draw()

    def _draw_transparent(self):
        self._mesh.draw_transparent()

    def _draw_mesh(self):
        self._mesh.draw()

    def _draw_transparent_mesh(self):
        self._mesh.draw_transparent()

    def _draw_nothing(self):
        pass

    @staticmethod
    def tear_down_matrix():
        glPopMatrix()

    def align_camera(self):
        glRotatef(-self.yaw, 0, 1, 0)

    def center_camera(self):
        glRotatef(-self.pitch, 1, 0, 0)
        glRotatef(-self.yaw, 0, 1, 0)
        glRotatef(-self.roll, 0, 0, 1)
        x, y, z = self.position
        glTranslated(-x, -y - 23, -z)

    def update_view_timer(self, dt):
        if self._mesh:
            self._mesh.timer(dt)
