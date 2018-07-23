from typing import List, Callable

from pyglet.gl import GL_LINES
from pyglet.graphics import draw
from pyglet.text import Label
from pyglet.window import key


class BaseButton(object):
    
    def __init__(self, drawable, left, right, bottom, top, func: Callable):
        self.drawable = drawable
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.func = func
        self.highlight = False
        self.v2i_bounding_box = ('v2i', [left, bottom, right, bottom, right, bottom, right, top,
                                         right, top, left, top, left, top, left, bottom])
        self.v2i_highlight_box = ('v2i', [left-1, bottom-1, right+1, bottom-1, right+1, bottom-1, right+1, top+1,
                                          right+1, top+1, left-1, top+1, left-1, top+1, left-1, bottom-1])
        self.c4B_bounding_box = ('c4B', [150, 150, 200, 255] * 8)
        self.c4B_highlight_box = ('c4B', [255, 255, 220, 255] * 8)

    @classmethod
    def labeled_button(cls, text, font_size, left, right, bottom, top, func: Callable):
        padding = int(font_size * 0.4)
        drawable = Label(text, font_name='Courier New', font_size=font_size, x=left + padding, y=bottom + padding)
        return cls(drawable, left, right, bottom, top, func)

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


class MenuComponent(object):
    def __init__(self, left, right, bottom, top):
        self.left, self.right, self.bottom, self.top = left, right, bottom, top

    def in_area(self, x, y):
        return (self.left < x < self.right) and (self.bottom < y < self.top)

    def draw(self):
        pass


class BaseMenu(object):
    
    def __init__(self, heading: str, buttons: List[BaseButton], x, y):
        self.heading = heading
        font_size = 50
        self.heading_label = Label(heading, font_name='Courier New', font_size=font_size, x=x, y=y + int(font_size / 2))
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
