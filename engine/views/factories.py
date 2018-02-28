from engine.views.ship_part import ShipPartView
from engine.views.ship import ShipView
from engine.models.ship_part import ShipPartModel
from engine.models.ship import ShipModel
from engine.models.base_model import BaseModel
from engine.models.projectiles import PlasmaModel
from engine.views.base_view import BaseView, DummyView
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon

from pywavefront import Wavefront
from engine.views.opengl_mesh import OpenGLWaveFrontFactory
from os import listdir, path


FILE_TEMPLATE = "objects/{}.obj"


class ViewFactory(object):

    def __init__(self, view_class=BaseView):
        self.meshes = {}
        files = [path.join("objects", file_name) for file_name in listdir('objects') if file_name.endswith('.obj')]
        self.mesh_factory = OpenGLWaveFrontFactory(files)
        self._view_class = view_class
        self.pre_factorized_views = []
        if view_class == BaseView:
            above_camera = MutableOffsets(0, -100, 0)
            zero = MutableOffsets(0, 0, 0)
            no_angle = MutableDegrees(0, 0, 0)
            bb = Polygon.manufacture([(0, 0)])
            self.dummy_model = BaseModel(position=above_camera, rotation=no_angle,
                                         movement=zero, spin=no_angle, bounding_box=bb)
            self.pre_factorized_views = [self._prefactorize() for i in range(200)]

    def _prefactorize(self):
        return self.manufacture(self.dummy_model)

    def repurpose(self, model: BaseModel) -> BaseView:
        view = self.pre_factorized_views.pop()
        if model.mesh is not None:
            view.set_mesh(self.mesh_factory.manufacture(model.mesh))
        view.set_model(model)
        print(len(self.pre_factorized_views), " views left")
        return view

    def manufacture(self, model: BaseModel) -> BaseView:
        if self.pre_factorized_views != []:
            return self.repurpose(model)
        if model.mesh is not None:
            mesh = self.mesh_factory.manufacture(model.mesh)
        else:
            mesh = None
        ship_view = self._view_class(model, mesh=mesh)
        return ship_view

    def manufacture_mesh(self, name) -> Wavefront:
        file_name = FILE_TEMPLATE.format(name)
        mesh = Wavefront(file_name)
        self.meshes[name] = mesh
        return mesh


class DummyViewFactory(ViewFactory):

    def __init__(self, view_class=DummyView):
        self._view = view_class()

    def repurpose(self, model: BaseModel) -> BaseView:
        return self._view

    def manufacture(self, model: BaseModel) -> BaseView:
        return self._view


class DynamicViewFactory(ViewFactory):

    model_view_map = {
        BaseModel: BaseView,
        ShipModel: ShipView,
        ShipPartModel: ShipPartView,
        PlasmaModel: BaseView
    }

    def manufacture(self, model: BaseModel):
        view_class = self.model_view_map[model.__class__]
        if model.mesh is not None:
            mesh = self.mesh_factory.manufacture(model.mesh)
        else:
            mesh = None
        ship_view = view_class(model, mesh=mesh)
        if hasattr(model, 'parts'):
            for part in model.parts:
                sub_view = self.manufacture(part)
                ship_view.add_sub_view(sub_view)
        return ship_view
