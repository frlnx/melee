from .base_view import BaseView
from engine.models.base_model import BaseModel
from .opengl_mesh import OpenGLTexturedFace, OpenGLMesh, OpenGLTexturedMaterial


class DynamicMeshView(BaseView):

    def __init__(self, model: BaseModel):
        super().__init__(model)
        faces = []
        material = OpenGLTexturedMaterial()
        for line in model.bounding_box.lines:
            OpenGLTexturedFace(vertices, texture_coords, normals, material)
        mesh = OpenGLMesh([], faces, name="Asteroid {}".format(model.uuid), group="Asteroids")
        self.set_mesh(mesh)