from collections import defaultdict
from itertools import chain
from typing import List, DefaultDict, Set, Tuple

from pyglet.graphics import Group, GL_N3F_V3F, GL_T2F_N3F_V3F, GL_V3F

from engine.views.opengl_mesh import OpenGLTexturedFace, OpenGLMaterial, OpenGLFace, OpenGLTexturedMaterial
from engine.views.wavefront_parsers import WaveFrontObject
from gui.views.component import ComponentView
from .drawable import Drawable


class MaterialGroup(Group):

    def __init__(self, material: OpenGLMaterial):
        super().__init__()
        self._material = material

    def set_state(self):
        self._material.set_material()


class XFace(OpenGLTexturedFace, Drawable):

    def __init__(self, vertices: list, normals: list, tex_coords: list, material: OpenGLMaterial):
        super().__init__(vertices, normals, tex_coords, material)
        self._material_group = MaterialGroup(material)

    @property
    def n_coordinates(self):
        return self.n_vertices

    @property
    def group(self):
        return self._material_group

    @property
    def normals(self):
        return self._normals

    @property
    def mode(self):
        return self.draw_mode

    @property
    def draw_data(self):
        return []

    @property
    def vertex_mode(self):
        return 'v3f'

    @property
    def vertices(self):
        return self._vertices

    @property
    def color_mode(self):
        return 'c3f'

    @property
    def colors(self):
        return []

    @property
    def normals_mode(self):
        return 'n3f'

    @property
    def tex_coord_mode(self):
        return 't2f'

    @property
    def tex_coords(self):
        return self._texture_coords


class MeshBundle(Drawable):

    def __init__(self, v3f: list, n3f: list=None, t2f: list=None, material_group: MaterialGroup=None):
        super().__init__()
        self._vertices = v3f
        self._normals = n3f
        self._tex_coords = t2f
        if t2f:
            self._draw_mode = GL_T2F_N3F_V3F
        elif n3f:
            self._draw_mode = GL_N3F_V3F
        else:
            self._draw_mode = GL_V3F
        self._material_group = material_group
        self._n_coordinates = int(len(v3f) / 3)

    @property
    def n_coordinates(self):
        return self._n_coordinates

    @property
    def group(self):
        return self._material_group

    @property
    def normals(self):
        return self._normals

    @property
    def mode(self):
        return self._draw_mode

    @property
    def draw_data(self):
        data = []
        for i in range(self.n_coordinates):
            if self._tex_coords:
                data += self.tex_coords[i * 2: i * 2 + 2]
            if self._normals:
                data += self.normals[i * 3: i * 3 + 3]
            data += self.vertices[i * 3: i * 3 + 3]
        return data

    @property
    def vertex_mode(self):
        return 'v3f'

    @property
    def vertices(self):
        return self._vertices

    @property
    def color_mode(self):
        return 'c3f'

    @property
    def colors(self):
        return []

    @property
    def normals_mode(self):
        return 'n3f'

    @property
    def tex_coord_mode(self):
        return 't2f'

    @property
    def tex_coords(self):
        return self._tex_coords


class XMesh(ComponentView, WaveFrontObject):

    def __init__(self, faces: List[OpenGLFace], textured_faces: List[OpenGLTexturedFace]):
        super().__init__(faces, textured_faces)
        face_index: DefaultDict[Tuple[int, OpenGLMaterial, MaterialGroup], Set[OpenGLFace]] = defaultdict(set)
        textured_face_index: DefaultDict[Tuple[int, OpenGLTexturedMaterial, MaterialGroup], Set[OpenGLTexturedFace]] = \
            defaultdict(set)
        for face in faces:
            face_index[(face.n_vertices, face.material, face.group)].add(face)
        for face in textured_faces:
            textured_face_index[(face.n_vertices, face.material, face.group)].add(face)
        self._drawables = []
        for (n_verticies, material, group), faces in face_index.items():
            v3f = list(chain(*[face.vertices for face in faces]))
            n3f = list(chain(*[face.normals for face in faces]))
            t2f = list(chain(*[face.texture_coords for face in faces]))
            drawable = MeshBundle(v3f, n3f, t2f, group)
            self._drawables.append(drawable)

    def drawables(self):
        return self._drawables

    def texts(self):
        return []
