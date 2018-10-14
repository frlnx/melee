from .component import MenuComponentModel


class ButtonModel(MenuComponentModel):

    controller_class = "ButtonController"
    view_class = "ButtonView"

    def __init__(self, left, right, bottom, top, func):
        super().__init__(left, right, bottom, top)
        self.func = func
        self._highlight = False

    def highlight(self, state: bool):
        self._highlight = state
        print(state)
        self._callback("highlight", state=state)
