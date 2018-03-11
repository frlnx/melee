from typing import List, Callable

from pyglet.graphics import draw
from pyglet.gl import GL_LINES
from pyglet.text import Label


class BaseButton(object):
    
    def __init__(self, drawable, left, right, bottom, top, function: Callable):
        self.drawable = drawable
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.function = function
        self.highlight = False
        self.v2i_bounding_box = ('v2i', [left, bottom, right, bottom, right, bottom, right, top,
                                         right, top, left, top, left, top, left, bottom])
        self.v2i_highlight_box = ('v2i', [left-1, bottom-1, right+1, bottom-1, right+1, bottom-1, right+1, top+1,
                                          right+1, top+1, left-1, top+1, left-1, top+1, left-1, bottom-1])
        self.c4B_bounding_box = ('c4B', [150, 150, 200, 255] * 8)
        self.c4B_highlight_box = ('c4B', [255, 255, 220, 255] * 8)

    @classmethod
    def labeled_button(cls, text, font_size, left, right, bottom, top, function: Callable):
        bottom_padding = int(font_size * 0.35)
        drawable = Label(text, font_name='Times New Roman', font_size=font_size, x=left, y=bottom + bottom_padding)
        return cls(drawable, left, right, bottom, top, function)

    def mouse_enter(self):
        self.highlight = True

    def mouse_leave(self):
        self.highlight = False

    def draw(self):
        self.drawable.draw()
        draw(8, GL_LINES, self.v2i_bounding_box, self.c4B_bounding_box)
        if self.highlight:
            draw(8, GL_LINES, self.v2i_highlight_box, self.c4B_highlight_box)
    
    def inside(self, x, y):
        return self.left < x < self.right and self.bottom < y < self.top


class BaseMenu(object):
    
    def __init__(self, heading: str, buttons: List[BaseButton], x, y):
        self.heading = heading
        self.heading_label = Label(heading, font_name='Times New Roman', font_size=50, x=x, y=y)
        self.buttons = buttons
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
                                               function=func)
            buttons.append(button)
        return cls(heading, buttons, x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            if button.inside(x, y):
                button.function()
                break

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            if button.inside(x, y) != button.inside(x - dx, y - dy):
                if button.inside(x, y):
                    button.mouse_enter()
                else:
                    button.mouse_leave()

    def draw(self):
        self.heading_label.draw()
        for button in self.buttons:
            button.draw()