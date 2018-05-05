from typing import List
import ctypes

from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.models.factories import ShipPartModelFactory
from engine.views.opengl_mesh import OpenGLWaveFrontFactory, OpenGLMesh

from math import hypot, atan2, degrees, cos, sin, radians
from itertools import chain

from pyglet.graphics import draw
from pyglet.gl import GL_LINES, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHTING, GL_LIGHT0, GL_AMBIENT, \
    GL_POSITION, GL_DIFFUSE
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glRotatef, glTranslatef, \
    glPopMatrix, glPushMatrix, glScalef, glEnable, glLightfv


class DrydockItem(object):
    def __init__(self, model: ShipPartModel, mesh: OpenGLMesh):
        self.model = model
        self.bbox = model.bounding_box.__copy__()
        self.mesh = mesh
        self.x, self.y, self.yaw = model.x, model.z, model.yaw
        self._to_cfloat_array = ctypes.c_float * 4
        self._highlight_part = False
        self._highlight_circle = False
        self._bb_color = (1., 1., 1., 0.1)

    def set_bb_color(self, *bb_color):
        self._bb_color = bb_color

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    def draw(self):
        glPushMatrix()
        self.draw_bb()
        self.draw_3d()
        self.draw_2d()
        glPopMatrix()

    def draw_3d(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(0.1, 0.1, 0.1, 0.1))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 1, -1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(13.0, 13.0, 13.0, 1.0))

        glTranslatef(self.x, 0, self.y)
        glRotatef(self.yaw, 0, 1, 0)
        if self._highlight_part:
            scale = 0.4
        else:
            scale = 0.25
        glScalef(scale, scale, scale)
        self.mesh.draw()
        glDisable(GL_LIGHTING)

    def draw_bb(self):
        glRotatef(90, 1, 0, 0)
        bb_v2f = list(chain(*[(l.x1, l.y1, l.x2, l.y2) for l in self.bbox.lines]))
        n_points = len(self.bbox.lines) * 2
        draw(n_points, GL_LINES, ('v2f', bb_v2f), ('c4f', self._bb_color * n_points))
        glRotatef(-90, 1, 0, 0)

    def draw_2d(self):
        pass


class DockableItem(DrydockItem):
    def __init__(self, model: ShipPartModel, mesh: OpenGLMesh):
        super().__init__(model, mesh)
        step = 36
        circle = [(cos(radians(d)), sin(radians(d)), cos(radians(d + step)), sin(radians(d + step))) for d in
                  range(0, 360, step)]
        self.circle = [x for x in chain(*circle)]
        self.v2f = ('v2f', self.circle)
        self.n_points = int(len(self.circle) / 2)
        self.c4B = ('c4B', [150, 200, 255, 128] * self.n_points)
        self.c4B_highlight = ('c4B', [0, 0, 255, 255] * self.n_points)

    def save(self):
        self.model.set_position_and_rotation(self.x, 0, self.y, 0, self.yaw, 0)

    def set_highlight(self, part=False, circle=False):
        self._highlight_part = part
        self._highlight_circle = circle

    def draw_2d(self):
        glRotatef(90, 1, 0, 0)
        if self._highlight_circle:
            scale = 4 * 0.4
        else:
            scale = 1
        glScalef(scale, scale, scale)
        if self._highlight_circle:
            draw(self.n_points, GL_LINES, self.v2f, self.c4B_highlight)
        else:
            draw(self.n_points, GL_LINES, self.v2f, self.c4B)

    def set_xy(self, x, y):
        self.x = x
        self.y = y
        self.bbox.set_position_rotation(self.x, self.y, self.yaw)

    def set_yaw(self, yaw):
        self.yaw = yaw
        self.bbox.set_position_rotation(self.x, self.y, self.yaw)


class NewGridItem(DockableItem):
    def __init__(self, model: ShipPartModel, mesh: OpenGLMesh):
        super(NewGridItem, self).__init__(model, mesh)
        self._draw_2d = self.draw_2d
        self.draw_2d = self.do_nothing
        self._set_xy = self.set_xy
        self.set_xy = self.place_on_ship
        self.place_on_ship = self.place_on_ship

    def copy(self):
        return self.__class__(self.model, self.mesh)

    def do_nothing(self):
        pass

    def place_on_ship(self, x, y):
        self._set_xy(x, y)
        self.place_on_ship = self._set_xy
        self.draw_2d = self._draw_2d


class Drydock(object):

    def __init__(self, ship: ShipModel, mesh_factory: OpenGLWaveFrontFactory):
        self.ship = ship
        self.mesh_factory = mesh_factory
        self.part_factory = ShipPartModelFactory()
        self.x_offset = 720
        self.y_offset = 360
        self.scale = 100
        self.gl_scale_f = [self.scale] * 3
        self._items = []
        for part in ship.parts:
            mesh = mesh_factory.manufacture(part.mesh_name)
            item = DockableItem(part, mesh)
            self._items.append(item)
        self.highlighted_item = self._items[0]
        self._held_item = None
        self.rotating = False
        self.moving = False
        self.mouse_x, self.mouse_y = 0, 0
        self._debug = False

    def debug(self):
        self._debug = True

    def reset(self):
        self._items = [self.manufacture_item("cockpit")]

    def manufacture_item(self, name):
        return DockableItem(self.part_factory.manufacture(name), self.mesh_factory.manufacture(name))

    @property
    def held_item(self) -> DockableItem:
        return self._held_item

    @property
    def items(self) -> List[DockableItem]:
        return self._items

    def save_all(self):
        for item in self.items:
            item.save()
        self.ship.set_parts({item.model for item in self.items})

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.held_item:
            if self.moving:
                self._held_item.set_xy(*self._screen_to_model(x, y))
            if self.rotating:
                mx, my = self._screen_to_model(x, y)
                dx, dy = mx - self.held_item.x, my - self.held_item.y
                self._held_item.set_yaw(degrees(atan2(dx, dy)))
            if self._held_item_legal_placement():
                self._held_item.set_bb_color(1., 1., 1., 0.1)
            else:
                self._held_item.set_bb_color(1., .2, .2, 0.1)
        else:
            distance = self.distance_to_item(self.highlighted_item, x, y)
            if distance < 50:
                self._held_item = self.highlighted_item
                if distance < 25:
                    self.moving = True
                else:
                    self.rotating = True

    def _held_item_legal_placement(self):
        for item in self.items:
            if item == self.held_item:
                continue
            intersects, x, y = item.bbox.intersection_point(self.held_item.bbox)
            if intersects:
                return False
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        self.moving = False
        self.rotating = False
        self._held_item = None

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x, self.mouse_y = x, y
        self.highlighted_item.set_highlight(False, False)
        self.highlighted_item = self.find_closest_item_to(x, y)
        distance = self.distance_to_item(self.highlighted_item, x, y)
        model_highlight = 0. <= distance < 25
        circle_highlight = 25. <= distance < 50
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
        return hypot(item.x * self.scale + self.x_offset - x, self.y_offset - y - item.y * self.scale)

    def _screen_to_model(self, x, y):
        return (x - self.x_offset) / self.scale, (self.y_offset - y) / self.scale

    def draw(self):
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.x_offset, -100, -self.y_offset)
        glScalef(*self.gl_scale_f)
        for item in self.items:
            item.draw()
        glDisable(GL_LIGHTING)
