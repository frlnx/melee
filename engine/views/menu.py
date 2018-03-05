from typing import List, Callable
import inspect
import pyglet
from engine.views.ship_part import ShipPartView
from engine.models.ship_part import ShipPartModel


class WidgetContainer(object):
    def __init__(self):
        self.widgets = []
        self.focus = None
        if len(self.widgets) > 0:
            self.set_focus(self.widgets[0])

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets:
            if widget.hit_test(x, y):
                self.set_focus(widget)
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

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                dir = 0

            self.set_focus(self.widgets[(i + dir) % len(self.widgets)])

            # elif symbol == pyglet.window.key.ESCAPE:
            #    pyglet.app.exit()

    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)


class Menu(WidgetContainer):
    def __init__(self, heading: str, items: List[Callable], x=200, y=600):
        super().__init__()
        self.heading = heading
        self.x = x
        self.y = y
        self.batch = pyglet.graphics.Batch()
        self.widgets = []
        self.buttons = [self.factorize(func, i) for i, func in enumerate(items)]
        self.highlightables = self.buttons
        if len(self.widgets) > 0:
            self.set_focus(self.widgets[0])
        self.label = pyglet.text.Label(heading, font_name='Times New Roman', font_size=50,
                                       x=self.x, y=self.y, batch=self.batch)


    def factorize(self, func, index, name=None):
        if name is None:
            name = func.__name__
            if name.startswith("_menu_"):
                name = name[6:]
            name = name.capitalize().replace('_', ' ')
        sig = inspect.signature(func)
        widgets = []
        y = self.y - (index + 1) * 55
        for x, (arg_name, params) in enumerate(sig.parameters.items()):
            default_text = params.default if params.default != inspect._empty else ""
            widget = TextWidget(default_text, self.x + (x + 1) * 310, y, 300, self.batch)
            widgets.append(widget)
        self.widgets += widgets  # ACHTUNG! SIDE EFFECT!!!
        menu_item = MenuItem(name, lambda: func(*[w.content for w in widgets]), self.x, y, self.batch)
        return menu_item

    def on_mouse_press(self, x, y, button, modifiers):
        super(Menu, self).on_mouse_press(x, y, button, modifiers)
        for button in self.buttons:
            if button.hit_test(x, y):
                button.func()
                break

    def on_mouse_motion(self, x, y, dx, dy):
        for highlightable in self.highlightables:
            highlightable.set_hightlight(highlightable.hit_test(x, y))

    def draw(self):
        self.batch.draw()
        for highlightable in self.highlightables:
            highlightable.draw()


class ShipConfigMenu(Menu):

    def __init__(self, ship_model, heading: str, items: List[Callable]):
        super().__init__(heading, items)
        self.ship_x = self.x + 640
        self.ship_y = self.y - 300
        self.ship_part_views = [self.factorize_ship_part(part_view) for part_view in ship_model._sub_views]
        for ship_part_view in self.ship_part_views:
            self.buttons += ship_part_view.buttons
        self.highlightables = self.buttons
        self._grid_left = self.ship_x / 110
        self._grid_right = (1280 - self.ship_x) / 110
        self._grid_up = (720 - self.ship_y) / 110
        self._grid_down = self.ship_y / 110


    def factorize_ship_part(self, part: ShipPartView):
        return MenuShipPartView(part, part._model,
                        part._model.x * 110 + self.ship_x, -part._model.z * 110 + self.ship_y,
                        self.batch, text=part._model.name[:3], width=100, height=100)

    def on_mouse_press(self, x, y, button, modifiers):
        for button in self.buttons:
            if button.hit_test(x, y):
                button.func()
                break

    def draw(self):
        super(ShipConfigMenu, self).draw()
        pyglet.gl.glDisable(pyglet.gl.GL_DEPTH_TEST)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_PROJECTION)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glOrtho(-self._grid_left, self._grid_right, -self._grid_up, self._grid_down, -1., 1000.)
        pyglet.gl.glMatrixMode(pyglet.gl.GL_MODELVIEW)
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glRotatef(90, 1, 0, 0)
        pyglet.gl.glTranslatef(0.5, -10, 0.5)
        for ship_part_view in self.ship_part_views:
            ship_part_view.draw_3d()


class MenuItem(object):
    def __init__(self, text: str, func: Callable, x, y, batch, width=300, height=50, font_size=36):
        self.text = text
        self.batch = batch
        self.func = func
        self.font_size = font_size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if text != '':
            pyglet.text.Label(text, font_name='Times New Roman', font_size=self.font_size,
                              x=self.x, y=self.y, batch=self.batch)
        pad = 1
        self.rectangle = Box(x - pad, y - pad, x + self.width + pad, y + self.height + pad, self.batch)
        self.highlight = False

    def hit_test(self, x, y):
        return (self.x < x < self.x + self.width and
                self.y < y < self.y + self.height)

    def set_hightlight(self, state):
        self.highlight = state

    def draw(self):
        if self.highlight:
            self.rectangle.draw_highlight()


class MenuShipPartView(MenuItem):

    def __init__(self, ship_part: ShipPartView, model: ShipPartModel, x, y, batch, text=None, width=100, height=100):
        if text is None:
            text = ''
        super().__init__(text, lambda: print("Klikk"), x, y, batch, width, height)
        self.ship_part = ship_part
        self.buttons = [MenuItem('rotate ->', lambda: model.rotate(0, 90, 0), x + width, y + 10, batch,
                                 width=30, height=10, font_size=10)]

    def draw_3d(self):
        self.ship_part.set_up_matrix()
        pyglet.gl.glScalef(0.25, 0.25, 0.25)
        self.ship_part._draw()
        self.ship_part.tear_down_matrix()


class Rectangle(object):
    '''Draws a rectangle into a batch.'''

    def __init__(self, x1, y1, x2, y2, batch):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
                                     ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
                                     ('c4B', [200, 200, 220, 255] * 4)
                                     )


class Box(object):
    def __init__(self, x1, y1, x2, y2, batch):
        self.v2i = ('v2i', [x1, y1, x2, y1, x2, y1, x2, y2, x2, y2, x1, y2, x1, y2, x1, y1])
        x1 -=1
        y1 -=1
        x2 +=1
        y2 +=1
        self.v2i_highlight = ('v2i', [x1, y1, x2, y1, x2, y1, x2, y2, x2, y2, x1, y2, x1, y2, x1, y1])
        self.c4B = ('c4B', [150, 150, 200, 255] * 8)
        self.c4B_highlight = ('c4B', [255, 255, 220, 255] * 8)
        self.vertex_list = batch.add(8, pyglet.gl.GL_LINES, None, self.v2i, self.c4B)

    def draw_highlight(self):
        pyglet.graphics.draw(8, pyglet.gl.GL_LINES, self.v2i_highlight, self.c4B_highlight)


class TextWidget(object):
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=(255, 255, 255, 255))
                                )
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Box(x - pad, y - pad, x + width + pad, y + height + pad, batch)

    @property
    def content(self):
        return self.document.text

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)
