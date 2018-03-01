from pyglet.gl import *
import pyglet
from ctypes import c_float
from collections import defaultdict
from typing import List, Tuple
import os

from engine.views.wavefront_parsers import WaveFrontObject, Face, TexturedFace, Material
from engine.views.wavefront_parsers import ObjectParser, WavefrontObjectFactory


class OpenGLMesh(WaveFrontObject):
    point_flag_map = {3: GL_TRIANGLES, 4: GL_QUADS}

    def __init__(self, faces: List['OpenGLFace'], textured_faces: List['OpenGLTexturedFace'], name=None, group=None):
        super().__init__(faces, textured_faces, name, group)
        self.n3f_v3f_by_material_n_points = defaultdict(lambda: defaultdict(list))
        self.t2f_n3f_v3f_by_material_n_points = defaultdict(lambda: defaultdict(list))
        self._sort_faces()
        self._convert_to_c_types()

    def _sort_faces(self):
        for face in self._faces:
            n_points = min(face.n_vertices, 5)
            self.n3f_v3f_by_material_n_points[face.material][n_points] += face.n3f_v3f
        for face in self._textured_faces:
            n_points = min(face.n_vertices, 5)
            self.t2f_n3f_v3f_by_material_n_points[face.material][n_points] += face.t2f_n3f_v3f

    def _convert_to_c_types(self):
        n3f_v3f_by_material_n_points = defaultdict(dict)
        for material, n_points_dict in self.n3f_v3f_by_material_n_points.items():
            for n_points, n3f_v3f_list in n_points_dict.items():
                n3f_v3f_by_material_n_points[material][n_points] = self._convert_c_float_arr(n3f_v3f_list)
        self.n3f_v3f_by_material_n_points = n3f_v3f_by_material_n_points
        t2f_n3f_v3f_by_material_n_points = defaultdict(dict)
        for material, n_points_dict in self.t2f_n3f_v3f_by_material_n_points.items():
            for n_points, t2f_n3f_v3f_list in n_points_dict.items():
                t2f_n3f_v3f_by_material_n_points[material][n_points] = self._convert_c_float_arr(t2f_n3f_v3f_list)
        self.t2f_n3f_v3f_by_material_n_points = t2f_n3f_v3f_by_material_n_points

    def _convert_c_float_arr(self, values: List) -> List[c_float]:
        c_arr = c_float * len(values)
        return c_arr(*values)

    def draw(self):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glDisable(GL_TEXTURE_2D)
        for material, n_points_dict in self.n3f_v3f_by_material_n_points.items():
            material.set_material()
            for n_points, n3f_v3f in n_points_dict.items():
                glInterleavedArrays(GL_N3F_V3F, 0, n3f_v3f)
                glDrawArrays(self.point_flag_map[n_points], 0, int(len(n3f_v3f) / 6))

        #glEnable(GL_TEXTURE_2D)
        for material, n_points_dict in self.t2f_n3f_v3f_by_material_n_points.items():
            material.set_material()
            for n_points, t2f_n3f_v3f in n_points_dict.items():
                glInterleavedArrays(GL_T2F_N3F_V3F, 0, t2f_n3f_v3f)
                glDrawArrays(self.point_flag_map[n_points], 0, int(len(t2f_n3f_v3f) / 8))
        glPopAttrib()
        glPopClientAttrib()

class OpenGLFace(Face):
    def __init__(self, vertices: list, normals: list, material: 'OpenGLMaterial'):
        super().__init__(vertices, normals, material)
        self.n3f_v3f = self._n3f_v3f()
        self.n_vertices = len(self._vertices)

    def _n3f_v3f(self):
        n3f_v3f = []
        for n, v in zip(self._normals, self._vertices):
            n3f_v3f += n
            n3f_v3f += v
        return n3f_v3f


class OpenGLTexturedFace(TexturedFace):
    def __init__(self, vertices: list, texture_coords: list, normals: list, material: 'OpenGLTexturedMaterial'):
        super().__init__(vertices, texture_coords, normals, material)
        self.t2f_n3f_v3f = self._t2f_n3f_v3f()

    def _t2f_n3f_v3f(self):
        t2f_n3f_v3f = []
        for n, t, v in zip(self._normals, self._texture_coords, self._vertices):
            t2f_n3f_v3f += n
            t2f_n3f_v3f += t
            t2f_n3f_v3f += v
        return t2f_n3f_v3f


class OpenGLMaterial(Material):
    def __init__(self, diffuse: Tuple[float, float, float], ambient: Tuple[float, float, float],
                 specular: Tuple[float, float, float], emissive: Tuple[float, float, float], shininess: float,
                 name: str, alpha: float=1.0):
        super().__init__(diffuse, ambient, specular, emissive, shininess, name, alpha)
        emissive = [e * d for e, d in zip(emissive, diffuse)]
        ambient = [a * d for a, d in zip(ambient, diffuse)]
        self.opengl_diffuse = self._convert_light_values(list(diffuse) + [alpha])
        self.opengl_ambient = self._convert_light_values(list(ambient) + [alpha])
        self.opengl_specular = self._convert_light_values(list(specular) + [alpha])
        self.opengl_emissive = self._convert_light_values(list(emissive) + [alpha])
        self.opengl_shininess = (shininess / 1000) * 128

    def _convert_light_values(self, values) -> List[c_float]:
        c_arr = (c_float * 4)
        return c_arr(*map(self._convert_zero_to_one_values_into_minus_one_to_one_values, values))

    @staticmethod
    def _convert_zero_to_one_values_into_minus_one_to_one_values(value: float) -> float:
        return value #* 2 - 1

    def set_material(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.opengl_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.opengl_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.opengl_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self.opengl_emissive)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.opengl_shininess)


class OpenGLTexturedMaterial(OpenGLMaterial):
    textures = {}
    def __init__(self, diffuse: Tuple[float, float, float], ambient: Tuple[float, float, float],
                 specular: Tuple[float, float, float], emissive: Tuple[float, float, float], shininess: float,
                 texture_file_name: str, name: str, alpha: float):
        super().__init__(diffuse, ambient, specular, emissive, shininess, name, alpha)
        self.texture_file_name = texture_file_name
        try:
            self.texture = self.textures[texture_file_name]
        except:
            try:
                self.texture = pyglet.image.load(texture_file_name).texture
            except FileNotFoundError:
                file_name = os.path.split(texture_file_name)[-1]
                local_path = os.path.join("objects", file_name)
                self.texture = pyglet.image.load(local_path).texture
            self.textures[texture_file_name] = self.texture
            assert self._value_is_a_power_of_two(self.texture.width)
            assert self._value_is_a_power_of_two(self.texture.height)

    @staticmethod
    def _value_is_a_power_of_two(value):
        return ((value & (value - 1)) == 0) and value != 0

    def set_material(self):
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)
        gl.glTexParameterf(self.texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameterf(self.texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        super(OpenGLTexturedMaterial, self).set_material()


class OpenGLWaveFrontParser(ObjectParser):
    def __init__(self):
        super().__init__(object_class=OpenGLMesh, face_class=OpenGLFace, textured_face_class=OpenGLTexturedFace,
                         material_class=OpenGLMaterial, textured_material_class=OpenGLTexturedMaterial)

class OpenGLWaveFrontFactory(WavefrontObjectFactory):

    def __init__(self, files_to_load: List[str]):
        super().__init__(files_to_load, object_parser_class=OpenGLWaveFrontParser)
