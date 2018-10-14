from .container import ComponentContainerController
from .drag_and_drop import DragAndDropController


class ContainerSwitcherController(ComponentContainerController):

    sub_controller_class = DragAndDropController

    def __init__(self, model):
        ComponentContainerController.__init__(self, model)

