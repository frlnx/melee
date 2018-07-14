import ctypes
import json
from functools import partial
from itertools import combinations
from math import hypot, atan2, degrees
from typing import Set, Callable

from pyglet.gl import GL_DEPTH_TEST, GL_MODELVIEW, GL_LIGHTING
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glRotatef, glTranslatef, glScalef
from pyglet.window.key import symbol_string, MOD_CTRL

from engine.models.base_model import PositionalModel
from engine.models.factories import ShipPartModelFactory
from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.views.factories import DynamicViewFactory
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
            self._view.set_mesh_scale(0.5)
        else:
            self._view.set_diffuse_multipliers(1., 1., 1., 1.)
            self._view.set_mesh_scale(0.25)

    @property
    def x(self):
        return self.model.x

    @property
    def y(self):
        return self.model.z

    @property
    def yaw(self):
        return self.model.yaw

    def draw(self):
        self._view.draw()

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
        self._view = view
        self.legal_move_func = legal_move_func or (lambda: True)
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

    def save(self):
        self.model.set_position_and_rotation(self.x, 0, self.y, 0, self.yaw, 0)

    def set_highlight(self, part=False, circle=False):
        super(DockableItem, self).set_highlight(part)
        self._highlight_circle = circle
        if circle:
            self._view.highlight_circle()
        else:
            self._view.lowlight_circle()

    def connect(self, other_part: "DrydockItem"):
        super(DockableItem, self).connect(other_part)
        self.update_status()
    
    def disconnect(self, other_part: "DrydockItem"):
        super(DockableItem, self).disconnect(other_part)
        self.update_status()

    def set_xy(self, x, y):
        o_x, o_y = self.x, self.y
        for new_x, new_y in [(x, y), (x, o_y), (o_x, y)]:
            self.model.set_position(new_x, 0, new_y)
            if self.legal_move_func(self):
                self.update()
                break
            else:
                self.model.set_position(o_x, 0, o_y)

    def set_yaw(self, yaw):
        o_yaw = self.yaw
        self.model.set_rotation(0, yaw, 0)
        if self.legal_move_func(self):
            self.update()
        else:
            self.model.set_rotation(0, o_yaw, 0)

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


class ShipConfiguration(object):
    default_part_view_class = ShipPartView
    default_item_class = DrydockItem

    def __init__(self, ship: ShipModel, view_factory: DynamicViewFactory):
        self.ship = ship
        self.view_factory = view_factory
        self.x_offset = 720
        self.y_offset = 360
        self.scale = 100
        self.gl_scale_f = [self.scale] * 3
        self._items = set()
        for part in ship.parts:
            item = self.item_from_model(part, view_class=self.default_part_view_class)
            self._items.add(item)
        self.highlighted_item = None

    def reset(self):
        pass

    def item_from_model(self, model, view_class=None):
        view_class = view_class or self.default_part_view_class
        view = self.view_factory.manufacture(model, view_class=view_class)
        view.set_mesh_scale(0.25)
        item = self.default_item_class(model, view)
        return item

    @property
    def items(self) -> set:
        return self._items

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

    def on_mouse_motion(self, x, y, dx, dy):
        if self.highlighted_item:
            self.highlighted_item.set_highlight(False, False)
        self.highlighted_item = self.find_closest_item_to(x, y)

    def find_closest_item_to(self, x, y):
        closest_item = None
        closest_distance = float('inf')
        for item in self.highlightables:
            distance = self.distance_to_item(item, x, y)
            if distance < closest_distance:
                closest_item = item
                closest_distance = distance
        return closest_item

    @property
    def highlightables(self):
        return self.items

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
        for item in self.highlightables:
            item.draw()
        glDisable(GL_LIGHTING)


class ControlConfiguration(ShipConfiguration):
    default_part_view_class = ShipPartConfigurationView
    default_item_class = ConfigurableItem

    def set_mode(self, mode):
        for item in self.items:
            item.set_mode(mode)

    def reset(self):
        for item in self.items:
            item.reset()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

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

    def on_mouse_motion(self, x, y, dx, dy):
        super(ControlConfiguration, self).on_mouse_motion(x, y, dx, dy)
        self.highlighted_item.set_highlight(True)


class Drydock(ShipConfiguration):
    default_part_view_class = ShipPartDrydockView
    default_item_class = DockableItem

    def __init__(self, ship: ShipModel, view_factory: DynamicViewFactory):
        super().__init__(ship, view_factory)
        self.part_factory = ShipPartModelFactory()
        self._update_connections()
        self._held_item = None
        self._new_items = self._build_new_items()

    @property
    def highlightables(self):
        return self.items | self._new_items

    def _build_new_items(self):
        new_items = set()
        for i, part_name in enumerate(self.part_factory.ship_parts):
            x = -self.x_offset / self.scale + i + 0.5
            y = self.y_offset / self.scale - 0.5
            model = PositionalModel(x=x, z=y, name=part_name)
            try:
                item = self.item_spawn_from_model(model)
            except KeyError:
                print("No mesh for {}, ignoring".format(part_name))
            else:
                new_items.add(item)
        return new_items

    def reset(self):
        self._items = {self.item_from_name("cockpit")}

    def item_from_name(self, name, model_class=None, view_class=None, position=None):
        model = self.part_factory.manufacture(name, model_class=model_class, position=position)
        item = self.item_from_model(model, view_class=view_class)
        return item

    def item_from_model(self, model, view_class=None):
        item = super(Drydock, self).item_from_model(model, view_class=view_class)
        item.legal_move_func = self._legal_placement
        item.observe(self._update_connections)
        return item

    def item_spawn_from_model(self, model):
        view = self.view_factory.manufacture(model, view_class=NewPartDrydockView)
        view.set_mesh_scale(0.25)
        spawn_func = partial(self.item_from_name, model.name, view_class=ShipPartDrydockView,
                             position=model.position)
        return ItemSpawn(model, view, spawn_func=spawn_func)

    @property
    def held_item(self) -> DockableItem:
        return self._held_item

    @property
    def items(self) -> Set[DockableItem]:
        return self._items

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if modifiers & MOD_CTRL:
            x = round(x / 10) * 10
            y = round(y / 10) * 10
        self.highlighted_item.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        if self.held_item:
            self._held_item.drag(*self._screen_to_model(x, y))
        else:
            distance = self.distance_to_item(self.highlighted_item, x, y)
            if distance < 50:
                self.grab(self.highlighted_item)
                self._held_item.drag(*self._screen_to_model(x, y))
                self._items.add(self.held_item)

    def grab(self, item: DockableItem):
        if self.highlighted_item != item:
            self.highlighted_item.set_highlight(False, False)
        if self.held_item:
            self.held_item.drop()
        self._held_item = item.grab()
        if self._held_item != self.highlighted_item:
            self.highlighted_item = self._held_item
            self._held_item.set_highlight(True)

    def _update_connections(self):
        for item1, item2 in combinations(self.items, 2):
            distance = hypot(item1.x - item2.x, item1.y - item2.y)
            if distance < 1.7:
                item1.connect(item2)
            else:
                item1.disconnect(item2)

    def _legal_placement(self, trial_item):
        for item in self.items:
            if item == trial_item:
                continue
            intersects, x, y = item.bbox.intersection_point(trial_item.bbox)
            if intersects:
                return False
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        if self._held_item:
            self._held_item.on_mouse_release(x, y, button, modifiers)
            self._held_item.drop()
            self._held_item = None

    def on_mouse_motion(self, x, y, dx, dy):
        if not self.held_item:
            if self.highlighted_item:
                self.highlighted_item.set_highlight(False, False)
            self.highlighted_item = self.find_closest_item_to(x, y)
            self.highlighted_item.on_mouse_motion(x, y, dx, dy)
            distance = self.distance_to_item(self.highlighted_item, x, y)
            model_highlight = 0. <= distance < 25
            circle_highlight = 25. <= distance < 50
            self.highlighted_item.set_highlight(model_highlight, circle_highlight)
