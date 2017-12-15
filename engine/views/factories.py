from engine.models.base_model import BaseModel
from engine.views.base_view import BaseView

from pywavefront import Wavefront


FILE_TEMPLATE = "objects/{}.obj"


class ViewFactory(object):

    def __init__(self, view_class):
        self.meshes = {}
        self._view_class = view_class

    def manufacture(self, model: BaseModel) -> BaseView:
        if model.mesh is not None:
            mesh = self.manufacture_mesh(model.mesh)
        else:
            mesh = None
        ship_view = self._view_class(model, mesh=mesh)
        return ship_view

    def manufacture_mesh(self, name) -> Wavefront:
        file_name = FILE_TEMPLATE.format(name)
        mesh = Wavefront(file_name)
        self.meshes[name] = mesh
        return mesh
