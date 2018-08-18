import ctypes
import json
from functools import partial
from math import hypot, atan2, degrees
from typing import Callable

from pyglet.gl import GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHTING, GL_LINES
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glRotatef, glTranslatef, glScalef, glPushMatrix, \
    glPopMatrix
from pyglet.graphics import draw
from pyglet.window.key import symbol_string

from engine.models.base_model import PositionalModel
from engine.models.factories import ShipPartModelFactory
from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.views.factories import DynamicViewFactory
from engine.views.menus.base import MenuComponent
from engine.views.ship import ShipView
from engine.views.ship_part import ShipPartDrydockView, NewPartDrydockView, ShipPartView, \
    ShipPartConfigurationView


class DrydockElement(object):

    # noinspection PyTypeChecker
    _to_cfloat_array: Callable = ctypes.c_float * 4

    def __init__(self, model: PositionalModel, view: ShipPartView):
        self.model = model
        self._view = view
        self._highlight = False

    def to_cfloat_array(self, *floats):
        return self._to_cfloat_array(*floats)

    def set_highlight(self, state, *_):
        self._highlight = state
        if state:
            self._view.set_diffuse_multipliers(2., 2., 2., 1.)
        else:
            self._view.set_diffuse_multipliers(1., 1., 1., 1.)

    @property
    def x(self):
        return self.model.x

    @property
    def y(self):
        return self.model.z

    @property
    def yaw(self):
        return self.model.yaw

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass


class DrydockItem(DrydockElement):
    def __init__(self, model: ShipPartModel, view: ShipPartDrydockView):
        super().__init__(model, view)
        self.model = model

    @property
    def bbox(self):
        return self.model.bounding_box

    def connect(self, other_part: "DrydockItem"):
        self.model.connect(other_part.model)

    def disconnect(self, other_part: "DrydockItem"):
        self.model.disconnect(other_part.model)

    @property
    def connected_items(self):
        return self.model.connected_parts


class ConfigurableItem(DrydockItem):

    def __init__(self, model: ShipPartModel, view: ShipPartConfigurationView):
        # noinspection PyTypeChecker
        super().__init__(model, view)
        self._view = view
        self._mouse_drag_origin = None

    def set_mode(self, mode):
        self._view.set_mode(mode)

    def on_key_press(self, symbol, modifiers):
        self.model.keyboard = symbol_string(symbol)
        self._view.update()

    def on_joybutton_press(self, joystick, button):
        self.model.button = button
        self._view.update()

    def on_joyaxis_motion(self, joystick, axis, value):
        if value == 1.0:
            self.model.axis = axis
        elif value == -1.0:
            self.model.axis = "-{}".format(axis)
        self._view.update()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._mouse_drag_origin = self._mouse_drag_origin or (x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if not self._mouse_drag_origin:
            return
        ox, oy = self._mouse_drag_origin
        self._mouse_drag_origin = None
        dx, dy = x - ox, y - oy
        mouse = []
        if dx > 50:
            mouse.append("x")
        elif dx < -50:
            mouse.append("-x")
        if dy > 50:
            mouse.append("y")
        elif dy < -50:
            mouse.append("-y")
        self.model.mouse = mouse
        self._view.update()

    def reset(self):
        self.model.mouse = []
        self.model.keyboard = None
        self.model.axis = None
        self.model.button = None
        self._view.update()


class DockableItem(DrydockItem):
    def __init__(self, model: ShipPartModel, view: ShipPartDrydockView, legal_move_func=None):
        super().__init__(model, view)
        self.model.observe(self.update_status, "working")
        self._view = view
        self.legal_move_func = legal_move_func or (lambda x: True)
        self._observers = set()
        self._highlight_circle = False
        self.update_status()
        self.held = False

    @property
    def moving(self):
        return self.held and self._highlight

    @property
    def rotating(self):
        return self.held and self._highlight_circle

    def observe(self, callback):
        self._observers.add(callback)

    def set_highlight(self, part=False, circle=False):
        super(DockableItem, self).set_highlight(part)
        self._highlight_circle = circle
        if circle:
            self._view.highlight_circle()
        elif part:
            self._view.lowlight_circle()
        else:
            self._view.hide_circle()

    def connect(self, other_part: "DrydockItem"):
        super(DockableItem, self).connect(other_part)
        self.update_status()
    
    def disconnect(self, other_part: "DrydockItem"):
        super(DockableItem, self).disconnect(other_part)
        self.update_status()

    def set_xy(self, x, y):
        o_x, o_y = self.x, self.y
        if o_x > x:
            o_x1 = o_x - 1
        else:
            o_x1 = o_x + 1

        if o_y > y:
            o_y1 = o_y - 1
        else:
            o_y1 = o_y + 1
        for new_x, new_y in [(x, y), (x, o_y1), (o_x1, y), (x, o_y), (o_x, y)]:
            self.model.teleport_to(new_x, 0, new_y)
            if self.is_legal_position:
                self.update()
                return
        self.model.teleport_to(o_x, 0, o_y)

    @property
    def is_legal_position(self):
        return self.legal_move_func(self)

    def set_yaw(self, yaw):
        o_yaw = self.yaw
        self.model.teleport_screw(0, yaw, 0)
        if self.legal_move_func(self):
            self.update()
        else:
            self.model.teleport_screw(0, o_yaw, 0)

    def grab(self):
        self.held = True
        return self

    def drag(self, x, y):
        if self.moving:
            self.set_xy(x, y)
        elif self.rotating:
            dx, dy = x - self.x, y - self.y
            self.set_yaw(degrees(atan2(dx, dy)))

    def drop(self):
        self.held = False

    def update(self):
        for observer in self._observers:
            observer()
        self.update_status()
        self.model.update()

    def update_status(self):
        if not self.model.connected_parts:
            effect_value = 0.0
        elif not self.model.working:
            effect_value = 0.1
        else:
            effect_value = 1.0
        self._view.set_diffuse_multipliers(1., effect_value, effect_value, 1.)
        inverse_effect_value = 1 - effect_value
        self._view.set_ambience_multipliers(.1 + inverse_effect_value, .1, .1, 1.0)
        self._view.set_effect_value(effect_value)


class ItemSpawn(DrydockElement):
    def __init__(self, model: PositionalModel, view: NewPartDrydockView, spawn_func=None):
        super().__init__(model, view)
        self.spawn_func = spawn_func

    def grab(self):
        self.set_highlight(False)
        new_item = self.spawn_func()
        new_item.set_highlight(True)
        return new_item.grab()


class ShipBuildMenuComponent(MenuComponent):

    def __init__(self, left, right, bottom, top, x_offset, y_offset):
        super().__init__(left, right, bottom, top)
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.v2i_bounding_box = ('v2i', [left, bottom, right, bottom, right, bottom, right, top,
                                         right, top, left, top, left, top, left, bottom])
        self.c4B_bounding_box = ('c4B', [150, 150, 200, 255] * 8)

    def grab(self, x, y) -> DockableItem:
        pass

    def drop(self, item: DockableItem):
        pass

    def drag(self, item, x, y, snap=False):
        pass

    def translate(self, x, y):
        pass

    def highlight_at(self, x, y):
        pass

    def draw(self):
        draw(8, GL_LINES, self.v2i_bounding_box, self.c4B_bounding_box)


class ShipPartDisplay(ShipBuildMenuComponent):
    default_part_view_class = ShipPartView
    default_item_class = DrydockItem

    def __init__(self, items: set, left, right, bottom, top, x, y, scale=25):
        super().__init__(left, right, bottom, top, x, y)
        self.scale = scale
        self.gl_scale_f = [scale] * 3
        self._items = items
        self._highlighted_item: DrydockItem = None

    @property
    def highlighted_item(self):
        return self._highlighted_item

    def set_highlighted_item(self, item):
        if self.highlighted_item:
            self._highlighted_item.set_highlight(False, False)
        self._highlighted_item = item

    def translate(self, x, y):
        self.x_offset += x
        self.y_offset += y

    def grab(self, x, y):
        item = self.find_closest_item_to(x, y)
        if item:
            return item.grab()

    @property
    def items(self) -> set:
        return self._items

    @property
    def highlightables(self):
        return self.items

    def highlight_at(self, x, y):
        self.set_highlighted_item(self.find_closest_item_to(x, y))

    def find_closest_item_to(self, x, y):
        closest_item = None
        closest_distance = float('inf')
        for item in self.highlightables:
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
        super(ShipPartDisplay, self).draw()
        glPushMatrix()
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(90, 1, 0, 0)
        glTranslatef(self.x_offset, -100, -self.y_offset)
        glScalef(*self.gl_scale_f)
        self._draw()
        glDisable(GL_LIGHTING)
        glPopMatrix()

    def _draw(self):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_key_press(self, symbol, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_joybutton_press(self, joystick, button):
        pass

    def on_joyaxis_motion(self, joystick, axis, value):
        pass


class ShipConfiguration(ShipPartDisplay):

    def __init__(self, left, right, bottom, top, ship: ShipModel, view_factory: DynamicViewFactory):
        self.ship = ship
        self.view_factory = view_factory
        self.ship_view: ShipView = view_factory.manufacture(ship, sub_view_class=self.default_part_view_class)
        items = set()
        for part_model in ship.parts:
            view = self.ship_view.get_sub_view(part_model.uuid)
            item = self.default_item_class(part_model, view)
            items.add(item)
        x = (right - left) / 2 + left
        y = (top - bottom) / 2 + bottom
        super().__init__(items, left, right, bottom, top, x, y)

    def _draw(self):
        super(ShipConfiguration, self)._draw()
        self.ship_view.draw()
        self.ship_view.draw_transparent()

    def reset(self):
        pass

    def set_highlighted_item(self, item):
        super(ShipConfiguration, self).set_highlighted_item(item)
        self._highlighted_item.set_highlight(True, False)

    def save_all(self):
        part_data = [
            {
                "position": list(item.model.position),
                "rotation": list(item.model.rotation),
                "name": item.model.name,
                "axis": item.model.axis,
                "button": item.model.button,
                "keyboard": item.model.keyboard
            } for item in self.items
        ]
        with open('ship.json', 'w') as fp:
            json.dump({"name": "ship", "parts": part_data}, fp)


class ControlConfiguration(ShipConfiguration):
    default_part_view_class = ShipPartConfigurationView
    default_item_class = ConfigurableItem
    _highlighted_item: ConfigurableItem

    def set_mode(self, mode):
        for item in self.items:
            item.set_mode(mode)

    def reset(self):
        for item in self.items:
            item.reset()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    @property
    def highlighted_item(self) -> ConfigurableItem:
        return self._highlighted_item

    def on_key_press(self, symbol, modifiers):
        if self.highlighted_item:
            self.highlighted_item.on_key_press(symbol, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        super(ControlConfiguration, self).on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if self.highlighted_item:
            self.highlighted_item.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        super(ControlConfiguration, self).on_mouse_release(x, y, button, modifiers)
        if self.highlighted_item:
            self.highlighted_item.on_mouse_release(x, y, button, modifiers)

    def on_joybutton_press(self, joystick, button):
        if self.highlighted_item:
            self.highlighted_item.on_joybutton_press(joystick, button)

    def on_joyaxis_motion(self, joystick, axis, value):
        if self.highlighted_item:
            self.highlighted_item.on_joyaxis_motion(joystick, axis, value)


class Drydock(ShipConfiguration):
    default_part_view_class = ShipPartDrydockView
    default_item_class = DockableItem

    def __init__(self, left, right, bottom, top, ship: ShipModel, view_factory: DynamicViewFactory):
        self.view_factory = view_factory
        self.original_model = ship
        ship = ship.copy()
        ship.set_position_and_rotation(0, 0, 0, 0, 0, 0)
        super().__init__(left, right, bottom, top, ship, view_factory)
        for item in self.items:
            item.legal_move_func = self._legal_placement

    def save_all(self):
        super(Drydock, self).save_all()
        self.original_model.set_parts({item.model for item in self.items})
        self.original_model.rebuild()

    def reset(self):
        for item in self.items.copy():
            if item.model.name == "cockpit":
                continue
            item.model.set_alive(False)
            self.remove_item(item)

    def drag(self, item, x, y, snap=False):
        if snap:
            x = round((x - self.x_offset) / 10) * 10 + self.x_offset
            y = round((y - self.y_offset) / 10) * 10 + self.y_offset
        if item:
            if item not in self.items:
                self.add_item(item)
            item.drag(*self._screen_to_model(x, y))

    def _legal_placement(self, trial_item):
        for item in self.items:
            if item == trial_item:
                continue
            if item.bbox.intersects(trial_item.bbox):
                return False
        return True

    def drop(self, item: DockableItem):
        if item:
            item.drop()

    def add_view_for(self, model):
        self.ship_view.add_sub_view(self.view_factory.manufacture(model))

    def add_item(self, item: DockableItem):
        item.legal_move_func = self._legal_placement
        item._view.set_mesh_scale(1.0)
        self.items.add(item)
        self.ship.add_part(item.model)
        self.add_view_for(item.model)

    def remove_item(self, item: DockableItem):
        self.items.remove(item)
        self.ship.remove_part(item.model)

    def highlight_at(self, x, y):
        super(Drydock, self).highlight_at(x, y)
        if self.highlighted_item:
            distance = self.distance_to_item(self.highlighted_item, x, y)
            model_highlight = 0. <= distance < 25
            circle_highlight = 25. <= distance < 50
            self.highlighted_item.set_highlight(model_highlight, circle_highlight)


class PartStore(ShipPartDisplay):
    default_part_view_class = ShipPartDrydockView
    default_item_class = DockableItem

    def __init__(self, left, right, bottom, top, view_factory: DynamicViewFactory):
        self.view_factory = view_factory
        self.part_factory = ShipPartModelFactory()
        self.x_offset = x = (right - left) / 2 + left
        self.y_offset = y = 0
        self.scale = 100
        super().__init__(self._build_new_items(), left, right, bottom, top, x, y)
        self.views = [item._view for item in self.items]

    def _draw(self):
        for item in self.views:
            item.draw()

    def _build_new_items(self):
        new_items = set()
        for i, part_name in enumerate(self.part_factory.ship_parts):
            x = 0
            y = -(i * 3) - 1
            model = PositionalModel(x=x, z=y, name=part_name)
            item = self.item_spawn_from_model(model)
            new_items.add(item)
        return new_items

    def translate(self, x, y):
        original_x_offset = self.x_offset
        super(PartStore, self).translate(x, y)
        self.x_offset = original_x_offset
        self.y_offset = max(min(200, self.y_offset), -100)

    def item_spawn_from_model(self, model):
        view: NewPartDrydockView = self.view_factory.manufacture(model, view_class=NewPartDrydockView)
        view.set_mesh_scale(1)
        spawn_func = partial(self.item_from_name, model.name, view_class=ShipPartDrydockView,
                             position=model.position)
        return ItemSpawn(model, view, spawn_func=spawn_func)

    def item_from_name(self, name, model_class=None, view_class=None, position=None):
        model = self.part_factory.manufacture(name, model_class=model_class, position=position)
        item = self.item_from_model(model, view_class=view_class)
        return item

    def item_from_model(self, model, view_class=None):
        view_class = view_class or self.default_part_view_class
        view: ShipPartDrydockView = self.view_factory.manufacture(model, view_class=view_class)
        view.set_mesh_scale(0.25)
        item = self.default_item_class(model, view)
        return item

    def drag(self, item, x, y, snap=False):
        pass

    def drop(self, item):
        pass
