from gui.models.container import ComponentContainerModel
from .component import MenuComponentController


class ComponentContainerController(MenuComponentController):

    model: ComponentContainerModel

    def __init__(self, model: ComponentContainerModel):
        super().__init__(model)
        self._components = []
        for model in self._model.components:
            self.add_component(model)
        model.observe(self.add_component, model.SIGNAL_ADD_COMPONENT)

    def add_component(self, component: ComponentContainerModel):
        from gui import controllers
        controller_class = getattr(controllers, component.controller_class)
        controller = controller_class(component)
        self._components.append(controller)

    def component_at(self, x, y):
        for component in self._components:
            if component.in_area(x, y):
                return component

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        component = self.component_at(x - dx, y - dy)
        if component:
            component.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        component = self.component_at(x, y)
        if component:
            component.on_mouse_release(x, y, button, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        component = self.component_at(x, y)
        if component:
            component.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        component = self.component_at(x, y)
        if component:
            component.on_mouse_press(x, y, button, modifiers)
