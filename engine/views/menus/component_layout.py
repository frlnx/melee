from typing import List

from pyglet.window import mouse
from pyglet.window.key import MOD_CTRL

from .base import MenuComponent


class ComponentLayout:
    
    def __init__(self, components: List[MenuComponent]):
        self._components = components
    
    def _component_at(self, x, y):
        for component in self._components:
            if component.in_area(x, y):
                return component

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        component = self._component_at(x, y)
        if component:
            if buttons & mouse.RIGHT:
                component.translate(dx, dy)
            if buttons & mouse.LEFT:
                if not self._held_item:
                    self._held_item = component.grab(x, y)
                else:
                    snap = modifiers & MOD_CTRL
                    component.drag(self._held_item, x, y, snap=snap)

    def on_mouse_release(self, x, y, button, modifiers):
        component = self._component_at(x, y)
        if component:
            component.drop(self._held_item)
            self._held_item = None

    def on_mouse_motion(self, x, y, dx, dy):
        component = self._component_at(x, y)
        if component:
            if not self._held_item:
                component.highlight_at(x, y)

    def draw(self):
        for component in self._components:
            component.draw()

    def draw_transparent(self):
        for component in self._components:
            component.draw_transparent()
