from typing import Dict, Tuple
from itertools import chain
from pyglet.graphics import draw
from pyglet.gl import GL_LINES, GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glOrtho, glRotatef, glTranslatef,\
    glPopMatrix, glPushMatrix, glScalef

from engine.models.ship import ShipModel


class GridItem(object):

    def __init__(self, model: ShipModel, draw_function):
        self.x = model.x
        self.y = model.z
        self.yaw = model.yaw
        self.draw_function = draw_function
        self.save_function = model.set_position_and_rotation

    def save(self):
        self.save_function(self.x, 0, self.y, 0, self.yaw, 0)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.y)
        glRotatef(self.yaw, 0, 1, 0)
        glScalef(0.25, 0.25, 0.25)
        self.draw_function()
        glPopMatrix()

    def set_xy(self, x, y):
        self.x = x
        self.y = y


class GridItemArranger(object):

    def __init__(self, x, y, items: Dict[Tuple[int, int], GridItem],
                 horizontal_slots=3, vertical_slots=3, slot_size=100):
        self.items = items
        self.held_item = None
        self.taken_from = (0, 0)
        self.x = x
        self.y = y
        self.width = horizontal_slots * slot_size
        self.height = vertical_slots * slot_size
        self._grid_left = self.x / slot_size
        self._grid_right = (1280 - self.x) / slot_size
        self._grid_up = (720 - self.y) / slot_size
        self._grid_down = self.y / slot_size
        self.horizontal_slots = horizontal_slots
        self.vertical_slots = vertical_slots
        self.slot_size = slot_size
        lines = [[line_x, y, line_x, y + self.vertical_slots] for line_x in range(horizontal_slots + 1)]
        lines += [[x, line_y, x + self.horizontal_slots, line_y] for line_y in range(vertical_slots + 1)]
        self.lines = ('v2i', list(chain(*lines)))
        self.n_lines = (horizontal_slots + 1) * 2 + (vertical_slots + 1) * 2
        self.line_colors = ('c4B', (220, 220, 220, 255) * self.n_lines)

    def draw(self):
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self._grid_left, self._grid_right, -self._grid_up, self._grid_down, -1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        draw(self.n_lines, GL_LINES, self.lines, self.line_colors)
        glRotatef(90, 1, 0, 0)
        glTranslatef(0.5, -10, 0.5)
        for item in self.items.values():
            item.draw()
        if self.held_item:
            self.held_item.draw()

    def save_all(self):
        for item in self.items.values():
            item.save()

    def _window_to_grid(self, x, y):
        x, y = self._window_to_grid_float(x, y)
        x = int(round(x))
        y = int(round(y))
        return x, y

    def _window_to_grid_float(self, x, y):
        x = (x - self.x) / self.slot_size - 0.5
        y = ((720 - self.y) - y) / self.slot_size - 0.5
        return x, y

    def drag(self, x, y):
        if self.held_item:
            x, y = self._window_to_grid_float(x, y)
            self.held_item.set_xy(x, y)
        else:
            x, y = self._window_to_grid(x, y)
            self.held_item = self.items.get((x, y))
            self.taken_from = (x, y)

    def drop(self, x, y):
        if self.held_item is None:
            return
        x, y = self._window_to_grid(x, y)
        if (x, y) not in self.items:
            self.held_item.set_xy(x, y)
            del self.items[self.taken_from]
            self.items[(x, y)] = self.held_item
            self.held_item = None
        else:
            self.items[self.taken_from] = self.items[(x, y)]
            self.items[(x, y)] = self.held_item
            self.held_item = None
