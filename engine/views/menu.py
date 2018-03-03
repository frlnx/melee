from typing import List, Tuple, Callable
import pyglet
from pyglet.gl import glMatrixMode, GL_PROJECTION, glLoadIdentity, glOrtho


class Menu(object):

    def __init__(self, heading: str, items: List[Tuple[str, Callable]]):
        self.heading = heading
        self.items = [MenuItem(*args, index=i) for i, args in enumerate(items)]

    def on_draw(self):
        for item in self.items:
            item.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        for item in self.items:
            item.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        pass


class MenuItem(object):

    def __init__(self, text: str, func: Callable, index: int):
        self.text = text
        self.func = func
        self.font_size = 36
        self.min_y = 100 - index * 50
        self.max_y = 100 - index * 50 + self.font_size
        self.label = pyglet.text.Label(text,
                          font_name='Times New Roman',
                          font_size=self.font_size,
                          x=200, y=self.min_y,
                          anchor_x='center', anchor_y='center')

    def draw(self):
        self.label.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.min_y < y < self.max_y:
            print(self.text)

    def on_mouse_release(self, x, y, button, modifiers):
        pass