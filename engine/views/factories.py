from engine.views.ship_part import ShipPartView
from engine.views.ship import ShipView
from engine.views.dynamic_mesh_view import DynamicMeshView
from engine.models.asteroid import AsteroidPartModel, AsteroidModel
from engine.models.ship_part import ShipPartModel
from engine.models.ship import ShipModel
from engine.models.base_model import BaseModel
from engine.models.projectiles import PlasmaModel
from engine.models.composite_model import CompositeModel
from engine.views.base_view import BaseView
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon


class ViewFactory(object):

    def __init__(self, mesh_factory, view_class=BaseView):
        self.meshes = {}
        self.mesh_factory = mesh_factory
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
        if model.mesh_name is not None:
            view.set_mesh(self.mesh_factory.manufacture(model.mesh_name))
        view.set_model(model)
        print(len(self.pre_factorized_views), " views left")
        return view

    def manufacture(self, model: BaseModel) -> BaseView:
        if self.pre_factorized_views != []:
            return self.repurpose(model)
        if model.mesh_name is not None:
            mesh = self.mesh_factory.manufacture(model.mesh_name)
        else:
            mesh = None
        ship_view = self._view_class(model, mesh=mesh)
        return ship_view


class DynamicViewFactory(ViewFactory):

    model_view_map = {
        BaseModel: BaseView,
        ShipModel: ShipView,
        ShipPartModel: ShipPartView,
        PlasmaModel: BaseView,
        AsteroidModel: DynamicMeshView,
        AsteroidPartModel: BaseView
    }

    def manufacture(self, model: BaseModel):
        view_class = self.model_view_map[model.__class__]
        if model.mesh_name is not None:
            mesh = self.mesh_factory.manufacture(model.mesh_name)
        else:
            mesh = None
        view = view_class(model, mesh=mesh)
        if hasattr(model, 'parts') and isinstance(model, CompositeModel):
            self.rebuild_subviews(view, model)
            model.observe_rebuild(lambda model: self.rebuild_subviews(view, model))
        return view

    def rebuild_subviews(self, ship_view: BaseView, model: CompositeModel):
        ship_view.clear_sub_views()
        for part in model.parts:
            sub_view = self.manufacture(part)
            ship_view.add_sub_view(sub_view)
