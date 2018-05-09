from typing import List
import ctypes

from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.models.factories import ShipPartModelFactory
from engine.views.opengl_mesh import OpenGLWaveFrontFactory, OpenGLMesh

from math import hypot, atan2, degrees, cos, sin, radians
from itertools import chain, combinations
from functools import partial

from pyglet.graphics import draw
from pyglet.gl import GL_LINES, GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHTING, GL_LIGHT0, GL_AMBIENT, \
    GL_POSITION, GL_DIFFUSE
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glRotatef, glTranslatef, \
    glPopMatrix, glPushMatrix, glScalef, glEnable, glLightfv


class DrydockElement(object):

    _to_cfloat_array = ctypes.c_float * 4

    def __init__(self, mesh: OpenGLMesh, x=0, y=0):
        self.mesh = mesh
        self._x = x
        self._y = y
        self._highlight_part = False

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def yaw(self):
        return 0

    def draw(self):
        glPushMatrix()
        self.draw_global_2d()
        self.light_on()
        self.localize()
        self.draw_local_3d()
        self.light_off()
        self.draw_local_2d()
        glPopMatrix()

    def localize(self):
        glTranslatef(self.x, 0, self.y)
        glRotatef(self.yaw, 0, 1, 0)

    def light_on(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.to_cfloat_array(0.1, 0.1, 0.1, 0.1))
        glLightfv(GL_LIGHT0, GL_POSITION, self.to_cfloat_array(0, 1, -1, 0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.to_cfloat_array(13.0, 13.0, 13.0, 1.0))

    @staticmethod
    def light_off():
        glDisable(GL_LIGHTING)

    def draw_local_3d(self):
        if self._highlight_part:
            scale = 0.4
        else:
            scale = 0.25
        glScalef(scale, scale, scale)
        self.mesh.draw()

    def draw_global_2d(self):
        pass

    def draw_local_2d(self):
        pass


class DrydockItem(DrydockElement):
    def __init__(self, model: ShipPartModel, mesh: OpenGLMesh):
        super().__init__(mesh)
        self.model = model
        self.bbox.set_position_rotation(self.x, self.y, -self.yaw)
        self._highlight_circle = False
        self._bb_color = [1., 1., 1., 0.1]
        self._light_color = self.to_cfloat_array(13., 13., 13., 1.)
        self._light_direction = self.to_cfloat_array(0, 1, -1, 0)
        self._light_ambience = self.to_cfloat_array(0.1, 0.1, 0.1, 0.1)

    @property
    def bbox(self):
        return self.model.bounding_box

    @property
    def x(self):
        return self.model.x

    @property
    def y(self):
        return self.model.z

    @property
    def yaw(self):
        return self.model.yaw

    def light_on(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self._light_ambience)
        glLightfv(GL_LIGHT0, GL_POSITION, self._light_direction)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self._light_color)

    def connect(self, other_part: "DrydockItem"):
        self.model.connect(other_part.model)

    def disconnect(self, other_part: "DrydockItem"):
        self.model.disconnect(other_part.model)

    def draw_global_2d(self):
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        bb_v2f = list(chain(*[(l.x1, l.y1, l.x2, l.y2) for l in self.bbox.lines]))
        n_points = len(self.bbox.lines) * 2
        draw(n_points, GL_LINES, ('v2f', bb_v2f), ('c4f', self._bb_color * n_points))

        lines = [(self.x, self.y, item.x, item.z) for item in self.connected_items]
        bb_v2f = list(chain(*lines))
        n_points = len(lines) * 2
        draw(n_points, GL_LINES, ('v2f', bb_v2f), ('c4f', [0.5, 0.7, 1.0, 1.0] * n_points))

        glPopMatrix()

    @property
    def connected_items(self):
        return self.model.connected_parts

    def set_bb_color(self, *bb_color):
        self._bb_color = bb_color


class DockableItem(DrydockItem):
    def __init__(self, model: ShipPartModel, mesh: OpenGLMesh):
        super().__init__(model, mesh)
        step = 36
        r_step = radians(step)
        ten_radians = [radians(d) for d in range(0, 360, step)]
        circle = [(cos(d), sin(d), cos(d + r_step), sin(d + r_step)) for d in ten_radians]
        self.circle = [x for x in chain(*circle)]
        self.v2f = ('v2f', self.circle)
        self.n_points = int(len(self.circle) / 2)
        self.c4B = ('c4B', [150, 200, 255, 128] * self.n_points)
        self.c4B_highlight = ('c4B', [0, 0, 255, 255] * self.n_points)
        self.update_status()

    def save(self):
        self.model.set_position_and_rotation(self.x, 0, self.y, 0, self.yaw, 0)

    def set_highlight(self, part=False, circle=False):
        self._highlight_part = part
        self._highlight_circle = circle

    def draw_local_2d(self):
        super(DockableItem, self).draw_local_2d()
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

    def connect(self, other_part: "DrydockItem"):
        super(DockableItem, self).connect(other_part)
        self.update_status()
    
    def disconnect(self, other_part: "DrydockItem"):
        super(DockableItem, self).disconnect(other_part)
        self.update_status()

    def set_xy(self, x, y):
        self.model.set_position(x, 0, y)
        self.update_status()

    def set_yaw(self, yaw):
        self.model.set_rotation(0, yaw, 0)

    def update_status(self):
        if not self.model.connected_parts:
            effect_value = 0.0
        elif not self.model.working:
            effect_value = 0.1
        else:
            effect_value = 1.0
        self._light_color = self.to_cfloat_array(13., 13. * effect_value, 13. * effect_value, 13.0)
        if self.model.material_affected:
            self.mesh.update_material(self.model.material_affected, self.model.material_mode,
                                      self.model.material_channel, effect_value)


class ItemSpawn(DrydockElement):
    def __init__(self, spawn_func, x, y, mesh):
        super().__init__(mesh, x, y)
        self.spawn_func = spawn_func
        self.mesh = mesh

    def get_item(self):
        return self.spawn_func()


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
        self._update_connections()
        self.highlighted_item = self._items[0]
        self._held_item = None
        self.rotating = False
        self.moving = False
        self._debug = False
        self._new_items = []
        for i, part_name in enumerate(self.part_factory.ship_parts):
            spawn_func = partial(self.new_item, part_name)
            x = -self.x_offset / self.scale + i + 0.5
            y = self.y_offset / self.scale - 0.5
            mesh = self.mesh_factory.manufacture(part_name)
            item = ItemSpawn(spawn_func, x, y, mesh)
            self._new_items.append(item)

    def new_item(self, name) -> DockableItem:
        model = self.part_factory.manufacture(name)
        mesh = self.mesh_factory.manufacture(name)
        item = DockableItem(model, mesh)
        self._held_item = item
        return item

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
                self.move_to(x, y)
            elif self.rotating:
                mx, my = self._screen_to_model(x, y)
                dx, dy = mx - self.held_item.x, my - self.held_item.y
                self.rotate_to(degrees(atan2(dx, dy)))
        else:
            distance = self.distance_to_item(self.highlighted_item, x, y)
            if distance < 50:
                self._held_item = self.highlighted_item
                self.moving = distance < 25
                self.rotating = not self.moving
            else:
                self._new_item_drag(x, y, dx, dy, buttons, modifiers)

    def _new_item_drag(self, x, y, dx, dy, buttons, modifiers):
        for item in self._new_items:
            distance = self.distance_to_item(item, x, y)
            if distance < 50:
                self.items.append(item.get_item())
                self.moving = True
                self.move_to(x, y)
                break


    def move_to(self, x, y):
        x, y = self._screen_to_model(x, y)
        self._move_x_to(x)
        self._move_y_to(y)

    def _move_x_to(self, x):
        o_x, o_y = self.held_item.x, self.held_item.y
        self._held_item.set_xy(x, self.held_item.y)
        if not self._held_item_legal_placement():
            self._held_item.set_xy(o_x, o_y)
        else:
            self._update_connections()

    def _move_y_to(self, y):
        o_x, o_y = self.held_item.x, self.held_item.y
        self._held_item.set_xy(self.held_item.x, y)
        if not self._held_item_legal_placement():
            self._held_item.set_xy(o_x, o_y)
        else:
            self._update_connections()

    def _update_connections(self):
        for item1, item2 in combinations(self.items, 2):
            distance = hypot(item1.x - item2.x, item1.y - item2.y)
            if distance < 1.7:
                item1.connect(item2)
            else:
                item1.disconnect(item2)

    def rotate_to(self, yaw):
        o_yaw = self.held_item.yaw
        self._held_item.set_yaw(yaw)
        if not self._held_item_legal_placement():
            self._held_item.set_yaw(o_yaw)

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
        if not self.held_item:
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
        for item in self._new_items:
            item.draw()
        glDisable(GL_LIGHTING)
