from engine.views.menus.base import BaseButton, BaseMenu
from typing import List, Callable
import pyglet
from pyglet.text import Label

import inspect


class InputBox(BaseButton):
    def __init__(self, field_name, left, right, bottom, top, default_text, cast_to):
        width = right - left
        font_size = 30
        field_name = field_name.capitalize()
        drawable = pyglet.graphics.Batch()
        self.cast_to = cast_to
        self.document = pyglet.text.document.UnformattedDocument(default_text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=(255, 255, 255, 255), font_size=font_size)
                                )
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=drawable)
        self.caret = pyglet.text.caret.Caret(self.layout, color=(255, 255, 255))
        self.layout.x = left + 10 #  (right - left) / 2 + left
        self.layout.y = bottom

        ingress_font_size = int(font_size / 3)
        text_y = top - 2 - ingress_font_size
        Label(field_name, font_name='Courier', font_size=ingress_font_size, x=left + 10, y=text_y, batch=drawable)
        def func():
            pass
        super().__init__(drawable, left, right, bottom, top, func)

    @property
    def content(self):
        return self.cast_to(self.document.text)


class InputMenu(BaseMenu):
    def __init__(self, heading: str, buttons: List[BaseButton], inputboxes: List[InputBox], x, y):
        super().__init__(heading, buttons, x, y)
        self.inputboxes = inputboxes
        self.focus = None
        if len(self.inputboxes) > 0:
            self.set_focus(self.inputboxes[0])

    @classmethod
    def input_menu(cls, heading, func_with_args, x, y, cancel_func, font_size=36):
        height = int(font_size * 1.6)
        width = int(height * 6)
        height_spacing = int(height * 1.1)
        buttons = []

        i = 1
        left = x
        right = x + width
        bottom = y - height_spacing * i
        top = y - height_spacing * i + height

        name = cancel_func.__name__
        if name.startswith("_menu_"):
            name = name[6:]
        name = name.capitalize().replace('_', ' ')
        button = BaseButton.labeled_button(name, font_size=font_size, left=left, right=right,
                                           bottom=bottom, top=top, func=cancel_func)
        buttons.append(button)
        sig = inspect.signature(func_with_args)
        inputboxes = []
        for i, (arg_name, params) in enumerate(sig.parameters.items()):
            i += 1
            left = x
            right = x + width
            bottom = y - height_spacing * (i + 1)
            top = y - height_spacing * (i + 1) + height

            default_text = params.default if params.default != inspect._empty else ""
            input_type = type(default_text)
            default_text = str(default_text)
            inputbox = InputBox(arg_name, left=left, right=right, bottom=bottom, top=top, default_text=default_text,
                                cast_to=input_type)
            inputboxes.append(inputbox)

        i += 2
        left = x
        right = x + width
        bottom = y - height_spacing * i
        top = y - height_spacing * i + height

        name = func_with_args.__name__
        if name.startswith("_menu_"):
            name = name[6:]
        name = name.capitalize().replace('_', ' ')
        prepared_func = lambda: func_with_args(*[inputbox.content for inputbox in inputboxes])
        button = BaseButton.labeled_button(name, font_size=font_size, left=left, right=right,
                                           bottom=bottom, top=top, func=prepared_func)
        buttons.append(button)
        return cls(heading, buttons, inputboxes, x, y)

    def draw(self):
        super(InputMenu, self).draw()
        for inputbox in self.inputboxes:
            inputbox.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        super(InputMenu, self).on_mouse_press(x, y, button, modifiers)
        for inputbox in self.inputboxes:
            if inputbox.inside(x, y):
                self.set_focus(inputbox)
                break
        else:
            self.set_focus(None)

        if self.focus:
            self.focus.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focus:
            self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if self.focus:
            self.focus.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focus:
            self.focus.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.TAB:
            if modifiers & pyglet.window.key.MOD_SHIFT:
                dir = -1
            else:
                dir = 1

            if self.focus in self.inputboxes:
                i = self.inputboxes.index(self.focus)
            else:
                i = 0
                dir = 0

            self.set_focus(self.inputboxes[(i + dir) % len(self.inputboxes)])

    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)