from math import hypot, atan2, degrees, cos, sin, radians
from typing import Dict, Tuple, List
from itertools import chain
from pyglet.graphics import draw
from pyglet.gl import GL_LINES, GL_DEPTH_TEST, GL_PROJECTION, GL_MODELVIEW
from pyglet.gl import glDisable, glMatrixMode, glLoadIdentity, glOrtho, glRotatef, glTranslatef,\
    glPopMatrix, glPushMatrix, glScalef


class GridItem(object):

    def __init__(self, x, y, yaw, save_Function, draw_function):
        self.x = x
        self.y = y
        self.yaw = yaw
        self.draw_function = draw_function
        self.save_function = save_Function
        step = 36
        circle = [(cos(radians(d)), sin(radians(d)), cos(radians(d + step)), sin(radians(d + step))) for d in range(0, 360, step)]
        self.circle = [x for x in chain(*circle)]
        self.v2f = ('v2f', self.circle)
        self.n_points = int(len(self.circle) / 2)
        self.c4B = ('c4B', [150, 200, 255, 128] * self.n_points)
        self.c4B_highlight = ('c4B', [0, 0, 255, 255] * self.n_points)
        self._highlight_part = False
        self._highlight_circle = False

    def save(self):
        self.save_function(self.x, 0, self.y, 0, self.yaw, 0)

    def set_highlight(self, part=False, circle=False):
        self._highlight_part = part
        self._highlight_circle = circle

    def draw(self):
        glPushMatrix()
        self.draw_3d()
        self.draw_2d()
        glPopMatrix()

    def draw_3d(self):
        glTranslatef(self.x, 0, self.y)
        glRotatef(self.yaw, 0, 1, 0)
        if self._highlight_part:
            scale = 0.4
        else:
            scale = 0.25
        glScalef(scale, scale, scale)
        self.draw_function()

    def draw_2d(self):
        glRotatef(-90, 1, 0, 0)
        if self._highlight_circle:
            scale = 4 * 0.4
        else:
            scale = 1
        glScalef(scale, scale, scale)
        if self._highlight_circle:
            draw(self.n_points, GL_LINES, self.v2f, self.c4B_highlight)
        else:
            draw(self.n_points, GL_LINES, self.v2f, self.c4B)

    def set_xy(self, x, y):
        self.x = x
        self.y = y

    def set_yaw(self, yaw):
        self.yaw = yaw


class NewGridItem(GridItem):

    def __init__(self, x, y, yaw, save_function, draw_function):
        super(NewGridItem, self).__init__(x, y, yaw, save_function, draw_function)
        self._draw_2d = self.draw_2d
        self.draw_2d = self.do_nothing
        self._set_xy = self.set_xy
        self.set_xy = self.place_on_ship
        self.place_on_ship = self.place_on_ship

    def do_nothing(self):
        pass

    def place_on_ship(self, x, y):
        self._set_xy(x, y)
        self.place_on_ship = self._set_xy
        self.draw_2d = self._draw_2d


class GridItemArranger(object):

    def __init__(self, x, y, items: Dict[Tuple[int, int], GridItem], new_items: Dict[Tuple[int, int], GridItem],
                 horizontal_slots=3, vertical_slots=3, slot_size=100):
        self.items = items
        self.held_item = None
        self.taken_from = None
        self.spinned_item = None
        self.spinning_around = (0, 0)
        self.x = x
        self.y = y
        self.width = horizontal_slots * slot_size
        self.height = vertical_slots * slot_size
        self._grid_left = self.x / slot_size
        self._grid_right = (1280 - self.x) / slot_size
        self._grid_up = (720 - self.y) / slot_size
        self._grid_down = self.y / slot_size
        self.new_items = new_items
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
        for new_item in self.new_items.values():
            new_item.draw()
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

    def move(self, x, y):
        if self.spinned_item or self.held_item:
            return
        for item in self.items.values():
            item.set_highlight(False, False)
        distance = self._off_grid_center(x, y)
        xy = (self._window_to_grid(x, y))
        item = self.items.get(xy)
        if item:
            item.set_highlight(distance < 0.4, distance > 0.4)
        new_item = self.new_items.get(xy)
        if new_item and not self.spinned_item:
            new_item.set_highlight(True, False)

    def drag(self, x, y):
        if self.held_item:
            x, y = self._window_to_grid_float(x, y)
            self.held_item.set_xy(x, y)
        elif self.spinned_item:
            x, y = self._window_to_grid_float(x, y)
            yaw = degrees(atan2(x - self.spinning_around[0], y - self.spinning_around[1]))
            self.spinned_item.set_yaw(yaw)
        else:
            off_center = self._off_grid_center(x, y)
            x, y = self._window_to_grid(x, y)
            if (x, y) in self.items:
                if off_center < 0.4:
                    self.held_item = self.items.get((x, y))
                    self.taken_from = (x, y)
                else:
                    self.spinned_item = self.items.get((x, y))
                    self.spinning_around = (x, y)
            elif (x, y) in self.new_items:
                self.held_item = self.new_items.get((x, y))

    def _off_grid_center(self, x, y):
        f_x, f_y = self._window_to_grid_float(x, y)
        i_x, i_y = self._window_to_grid(x, y)
        return hypot(f_x - i_x, f_y - i_y)
        
    def drop(self, x, y):
        self.spinned_item = None
        if self.held_item is None:
            return
        x, y = self._window_to_grid(x, y)
        if self.taken_from:
            if (x, y) not in self.items:
                self.held_item.set_xy(x, y)
                del self.items[self.taken_from]
            else:
                self.items[self.taken_from] = self.items[(x, y)]
            self.items[(x, y)] = self.held_item
        else:
            if (x, y) not in self.items:
                self.held_item.set_xy(x, y)
                self.items[(x, y)] = self.held_item
        self.held_item = None
        self.taken_from = None
