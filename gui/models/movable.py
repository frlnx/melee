from .component import MenuComponentModel


class MovableMixin(MenuComponentModel):

    controller_class = "DragControllerMixin"

    def move(self, dx, dy):
        self._left += dx
        self._right += dx
        self.center_x += dx
        self._top += dy
        self._bottom += dy
        self.center_y += dy
        self._callback("move")
