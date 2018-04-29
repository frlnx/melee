from typing import List
from math import hypot, atan2
import ctypes

from pyglet.text import Label
from pyglet.window import key as keymap
from pyglet.graphics import draw
from pyglet.gl import GL_LINES, GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW, GL_LIGHTING, GL_LIGHT0, GL_AMBIENT, \
    GL_POSITION, GL_DIFFUSE
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glOrtho, glRotatef, glTranslatef, \
    glPopMatrix, glPushMatrix, glScalef, glEnable, glLightfv, GLfloat

from .grid import MovableGridItem
from engine.models.ship import ShipModel
from engine.views.opengl_mesh import OpenGLWaveFrontFactory


class Drydock(object):

    def __init__(self, ship: ShipModel, mesh_factory: OpenGLWaveFrontFactory):
        self.scale = 100
        self.gl_scale_f = [self.scale] * 3
        self._items = []
        self._to_cfloat_array = ctypes.c_float * 4
        for part in ship.parts:
            draw_function = mesh_factory.manufacture(part.mesh_name).draw
            item = MovableGridItem(part.x, part.z, part.yaw,
                                   part.set_position_and_rotation, draw_function=draw_function)
            self._items.append(item)
        self.highlighted_item = self._items[0]
        self.held_item = None
        self.rotating =  False
        self.moving = False
        self.mouse_x, self.mouse_y = 0, 0

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    @property
    def items(self) -> List[MovableGridItem]:
        return self._items

    def save_all(self):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x, self.mouse_y = x, y
        self.highlighted_item.set_highlight(False, False)
        self.highlighted_item = self.find_closest_item_to(x, y)
        distance = self.distance_to_item(self.highlighted_item, x, y)
        model_highlight = 0 <= distance < 25
        circle_highlight = 25 <= distance < 50
        self.highlighted_item.set_highlight(model_highlight, circle_highlight)

    def find_closest_item_to(self, x, y):
        closest_item = None
        closest_distance = 9999999999999999999
        for item in self.items:
            distance = self.distance_to_item(item, x, y)
            if distance < closest_distance:
                closest_item = item
                closest_distance = distance
        return closest_item

    def distance_to_item(self, item, x, y):
        return hypot(item.x * self.scale + 720 - x, 360 - y - item.y * self.scale)

    def draw(self):
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glRotatef(90, 1, 0, 0)
        glTranslatef(720, -100, -360)
        glScalef(*self.gl_scale_f)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(0.1, 0.1, 0.1, 1.0))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 0.3, 1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(3.0, 3.0, 3.0, 1.0))
        for item in self.items:
            item.draw()
            item.draw_text()
        glDisable(GL_LIGHTING)


    # def draw_text(self):
    #     glMatrixMode(GL_PROJECTION)
    #     glLoadIdentity()
    #     glOrtho(0, 1280, 0, 720, -1., 1000.)
    #     glMatrixMode(GL_MODELVIEW)
    #     glLoadIdentity()
    #     for item in self.items:
    #         item.draw_text()