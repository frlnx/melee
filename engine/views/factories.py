from functools import partial
from math import cos, sin, radians

from engine.models.asteroid import AsteroidModel
from engine.models.base_model import BaseModel, PositionalModel
from engine.models.composite_model import CompositeModel
from engine.models.projectiles import PlasmaModel
from engine.models.shield import ShieldModel
from engine.models.ship import ShipModel
from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees
from engine.physics.polygon import Polygon
from engine.views.base_view import BaseView
from engine.views.ship import ShipView
from engine.views.ship_part import ShipPartView
from .opengl_mesh import OpenGLTexturedFace, OpenGLTexturedMaterial, OpenGLMesh, OpenGLMaterial, OpenGLFace


class ViewFactory(object):
    _point_seven = (0.7, 0.7, 0.7)
    _zeroes = (0, 0, 0)
    model_mesh_map = {
        AsteroidModel: {"method": "_spheroid",
                        "material": partial(OpenGLTexturedMaterial, texture_file_name="ROCKS002.TGA",
                                            diffuse=(0.7, 0.7, 0.7), name="Rock Surface")},
        ShieldModel: {"method": "_hexagon_fence",
                      "material": partial(OpenGLMaterial, diffuse=(0, 0, 0), emissive=(.54, .81, .94),
                                          alpha=.5, name="Shield")}
    }

    def __init__(self, mesh_factory, view_class=BaseView):
        self.meshes = {}
        self.mesh_factory = mesh_factory
        self._view_class = view_class
        self.pre_factorized_views = []
        if view_class == BaseView:
            above_camera = MutableOffsets(0, -100, 0)
            zero = MutableOffsets(0, 0, 0)
            no_angle = MutableDegrees(0, 0, 0)
            no_acceleration = MutableOffsets(0, 0, 0)
            no_torque = MutableDegrees(0, 0, 0)
            bb = Polygon.manufacture([(0, 0)])
            self.dummy_model = BaseModel(position=above_camera, rotation=no_angle,
                                         movement=zero, spin=no_angle, acceleration=no_acceleration,
                                         torque=no_torque, bounding_box=bb)
            self.pre_factorized_views = [self._prefactorize() for i in range(200)]

    def _prefactorize(self):
        return self.manufacture(self.dummy_model)

    def repurpose(self, model: BaseModel) -> BaseView:
        view = self.pre_factorized_views.pop()
        if model.mesh_name is not None:
            view.set_mesh(self._mesh_for_model(model))
        view.set_model(model)
        print(len(self.pre_factorized_views), " views left")
        return view

    def _mesh_for_model(self, model):
        config = self.model_mesh_map.get(model.__class__, {})
        func_name = config.get('method', "_mesh_by_name")
        func = getattr(self, func_name, self._mesh_by_name)
        return func(model, **config)

    def _mesh_by_name(self, model):
        if model.mesh_name is None:
            return None
        return self.mesh_factory.manufacture(model.mesh_name)

    def _spheroid(self, model, **config):
        faces = []
        material = config['material']()
        bb = model.bounding_box
        for line_nr, line in enumerate(bb.lines):
            middle_factor = sin(radians(45))
            middle_x1 = line.original_x1 * middle_factor
            middle_y1 = line.original_y1 * middle_factor
            middle_x2 = line.original_x2 * middle_factor
            middle_y2 = line.original_y2 * middle_factor
            vertices = [(line.original_x1, 0, line.original_y1),
                        (line.original_x2, 0, line.original_y2),
                        (middle_x2, 10, middle_y2),
                        (middle_x1, 10, middle_y1)]
            texture_x1 = line_nr % 2
            texture_x2 = (line_nr + 1) % 2
            texture_coords = [(texture_x1, 0), (texture_x2, 0), (texture_x2, 1), (texture_x1, 1)]
            face = OpenGLTexturedFace(vertices, texture_coords, vertices, material)
            faces.append(face)
            vertices = [(middle_x1, -10, middle_y1),
                        (middle_x2, -10, middle_y2),
                        (line.original_x2, 0, line.original_y2),
                        (line.original_x1, 0, line.original_y1)]
            texture_coords = [(texture_x1, 1), (texture_x2, 1), (texture_x2, 0), (texture_x1, 0)]
            face = OpenGLTexturedFace(vertices, texture_coords, vertices, material)
            faces.append(face)
            vertices = [(middle_x1, 10, middle_y1),
                        (middle_x2, 10, middle_y2),
                        (bb.x, 15, bb.y)]
            texture_coords = [(texture_x1, 1), (texture_x2, 1), (0.5, 0)]
            face = OpenGLTexturedFace(vertices, texture_coords, vertices, material)
            faces.append(face)
        mesh = OpenGLMesh([], faces, name="Asteroid {}".format(model.uuid), group="Asteroids")
        return mesh

    def _hexagon_fence(self, model, **config):
        faces = []
        material = config['material']()
        for line in model.bounding_box.lines:
            c_x, c_z = line.centroid
            c_y = 0
            half_length = line.length / 2
            r = line.radii + radians(90)
            normals = [(cos(r), 0, sin(r))] * 3
            hex_points = [(c_x, 1, c_z), (line.x1, half_length, line.y1), (line.x1, -half_length, line.y1),
                          (c_x, -1, c_z), (line.x2, -half_length, line.y2), (line.x2, half_length, line.y2)]
            coords1 = hex_points[-1]
            for coords2 in hex_points:
                vertices = [(c_x, c_y, c_z), coords1, coords2]
                coords1 = coords2
                face = OpenGLFace(vertices, normals, material)
                faces.append(face)
        mesh = OpenGLMesh(faces, [], name="Shield", group="Shields")
        return mesh

    def manufacture(self, model: BaseModel) -> BaseView:
        if self.pre_factorized_views:
            return self.repurpose(model)
        mesh = self._mesh_for_model(model)
        ship_view = self._view_class(model, mesh=mesh)
        return ship_view


class DynamicViewFactory(ViewFactory):
    model_view_map = {
        PositionalModel: BaseView,
        BaseModel: BaseView,
        ShipModel: ShipView,
        ShipPartModel: ShipPartView,
        PlasmaModel: BaseView,
        AsteroidModel: BaseView,
        ShieldModel: BaseView
    }

    def manufacture(self, model: PositionalModel, view_class=None):
        view_class = view_class or self.model_view_map[model.__class__]
        mesh = self._mesh_for_model(model)
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
