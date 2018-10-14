from .component import MenuComponentModel


class ScrollerModelMixin(MenuComponentModel):

    def __init__(self, scroll_x=0, scroll_y=0):
        self._scroll_x = scroll_x
        self._scroll_y = scroll_y

    def scroll_by(self, dx, dy):
        self._scroll_x += dx
        self._scroll_y += dy
        self._callback('scroll')

    def scroll_to(self, scroll_x, scroll_y):
        self._scroll_x = scroll_x
        self._scroll_y = scroll_y
        self._callback('scroll')
