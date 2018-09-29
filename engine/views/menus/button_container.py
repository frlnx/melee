from typing import List, Callable

from pyglet.text import Label
from pyglet.window import key

from .base import OrthoMenuComponent, BaseButton


class ButtonContainer(OrthoMenuComponent):

    def __init__(self, heading, buttons, left, right, bottom, top):
        super().__init__(left, right, bottom, top)
        self.heading = heading
        font_size = 50
        x = left
        y = bottom
        self.heading_label = Label(heading, font_name='Courier New', font_size=font_size,
                                   x=left, y=y + int(font_size / 2))
        self.buttons = buttons
        self.highlightables = list(buttons)
        self.x = x
        self.y = y

    @classmethod
    def labeled_menu_from_function_names(cls, heading, callables: List[Callable], x, y, font_size=36):
        height = int(font_size * 1.6)
        width = int(height * 6)
        height_spacing = int(height * 1.1)
        buttons = []
        for i, func in enumerate(callables):
            i += 1
            name = func.__name__
            if name.startswith("_menu_"):
                name = name[6:]
            name = name.capitalize().replace('_', ' ')
            button = BaseButton.labeled_button(name, font_size=font_size, left=x, right=x + width,
                                               bottom=y - height_spacing * i, top=y - height_spacing * i + height,
                                               func=func)
            buttons.append(button)
        return cls(heading, buttons, x, y)

    def on_key_press(self, symbol, modifiers):
        option_id = symbol - key._1
        try:
            self.buttons[option_id].func()
        except IndexError:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            if button.inside(x, y):
                button.func()
                break

    def on_mouse_motion(self, x, y, dx, dy):
        for element in self.highlightables:
            # if element.inside(x, y) != element.inside(x - dx, y - dy):
            if element.inside(x, y):
                element.mouse_enter()
            else:
                element.mouse_leave()

    def draw(self):
        self.heading_label.draw()
        for button in self.buttons:
            button.draw()
