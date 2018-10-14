from engine.models.observable import Observable


class MenuComponentModel(Observable):

    controller_class = None
    view_class = None

    def __init__(self, left, right, bottom, top):
        Observable.__init__(self)
        self._left, self._right, self._bottom, self._top = left, right, bottom, top
        self.width = self.right - self.left
        self.center_x = self.width / 2 + self.left
        self.height = self._top - self._bottom
        self.center_y = self.height / 2 + self.bottom
        self.aspect_ratio = float(self.width) / self.height
        self._animation_timer = 0.

    def in_area(self, x, y):
        return (self.left <= x <= self.right) and (self.bottom <= y <= self.top)

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    @property
    def bottom(self):
        return self._bottom

    @property
    def top(self):
        return self._top
