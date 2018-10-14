from typing import List

from .component import MenuComponentModel


class ComponentContainerModel(MenuComponentModel):

    SIGNAL_ADD_COMPONENT = 1

    def __init__(self, components: List[MenuComponentModel], left, right, bottom, top):
        super().__init__(left, right, bottom, top)
        self._components = components

    def add_component(self, model):
        self._components.append(model)
        self._callback(self.SIGNAL_ADD_COMPONENT, component=model)

    @property
    def components(self):
        return self._components

    def component_at(self, x, y):
        for component in self._components:
            if component.in_area(x, y):
                return component
