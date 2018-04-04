from pyglet.gl import *
import pyglet
from ctypes import c_float
from collections import defaultdict
from itertools import chain
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
        self.materials = {face.material.name: face.material for face in faces}
        self.materials.update({face.material.name: face.material for face in textured_faces})
        self._sort_faces()
        self._convert_to_c_types()

    def update_material(self, material_name, material_mode, material_channel, value):
        channels = 'rgba'
        values = [int(channel not in material_channel) or value for channel in channels]
        self.materials[material_name].update(**{material_mode: values})

    def __copy__(self):
        copy = self.__class__(self._faces, self._textured_faces, name=self.name, group=self.group)
        copy.materials = {material.name: material.__copy__() for material in self.materials.values()}
        copy.n3f_v3f_by_material_n_points = {copy.materials[material.name]: obj for material, obj in copy.n3f_v3f_by_material_n_points.items()}
        copy.t2f_n3f_v3f_by_material_n_points = {copy.materials[material.name]: obj for material, obj in copy.t2f_n3f_v3f_by_material_n_points.items()}
        return copy

    def _sort_faces(self):
        for face in self._faces:
            n_points = min(face.n_vertices, 5)
            material = self.materials[face.material.name]
            self.n3f_v3f_by_material_n_points[material][n_points] += face.n3f_v3f
        for face in self._textured_faces:
            n_points = min(face.n_vertices, 5)
            material = self.materials[face.material.name]
            self.t2f_n3f_v3f_by_material_n_points[material][n_points] += face.t2f_n3f_v3f

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
        self.t2f_v3f = self._t2f_v3f()

    def _t2f_n3f_v3f(self):
        t2f_n3f_v3f = []
        for n, t, v in zip(self._normals, self._texture_coords, self._vertices):
            t2f_n3f_v3f += t
            t2f_n3f_v3f += n
            t2f_n3f_v3f += v
        return t2f_n3f_v3f

    def _t2f_v3f(self):
        t2f_v3f = []
        for t, v in zip(self._texture_coords, self._vertices):
            t2f_v3f += t
            t2f_v3f += v
        return t2f_v3f


class OpenGLMaterial(Material):
    def __init__(self, diffuse: Tuple[float, float, float], ambient: Tuple[float, float, float],
                 specular: Tuple[float, float, float], emissive: Tuple[float, float, float], shininess: float,
                 name: str, alpha: float=1.0):
        super().__init__(diffuse, ambient, specular, emissive, shininess, name, alpha)
        emissive = [e * d for e, d in zip(emissive, diffuse)]
        ambient = [a * d for a, d in zip(ambient, diffuse)]
        self.opengl_diffuse = self.to_c_arr(list(diffuse) + [alpha])
        self.opengl_ambient = self.to_c_arr(list(ambient) + [alpha])
        self.opengl_specular = self.to_c_arr(list(specular) + [alpha])
        self.opengl_emissive = self.to_c_arr(list(emissive) + [alpha])
        self.opengl_shininess = (shininess / 1000) * 128
        self.original_opengl_diffuse = self.opengl_diffuse
        self.original_opengl_ambient = self.opengl_ambient
        self.original_opengl_specular = self.opengl_specular
        self.original_opengl_emissive = self.opengl_emissive
        self.original_opengl_shininess = self.opengl_shininess

    def update(self, **kwargs):
        ones = (1, 1, 1, 1)
        opengl_diffuse = [a * b for a, b in zip(kwargs.get('diffuse', ones), self.original_opengl_diffuse)]
        self.opengl_diffuse = self.to_c_arr(opengl_diffuse)
        self.opengl_ambient = self.to_c_arr((a * b for a, b in zip(kwargs.get('ambient', ones), self.original_opengl_ambient)))
        self.opengl_specular = self.to_c_arr((a * b for a, b in zip(kwargs.get('specular', ones), self.original_opengl_specular)))
        self.opengl_emissive = self.to_c_arr((a * b for a, b in zip(kwargs.get('emissive', ones), self.original_opengl_emissive)))
        self.opengl_shininess = (kwargs.get('shininess', self.original_opengl_shininess) / 1000) * 128

    def __copy__(self):
        return self.__class__(diffuse=self.diffuse, ambient=self.ambient, specular=self.specular,
                              emissive=self.emissive, shininess=self.shininess, name=self.name, alpha=self.alpha)

    @staticmethod
    def to_c_arr(values) -> List[c_float]:
        c_arr = (c_float * 4)
        return c_arr(*values)

    @staticmethod
    def _convert_zero_to_one_values_into_minus_one_to_one_values(value: float) -> float:
        return value #* 2 - 1

    def set_material(self):
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.opengl_diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.opengl_ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.opengl_specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self.opengl_emissive)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.opengl_shininess)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


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
                image = pyglet.image.load(texture_file_name)
            except FileNotFoundError:
                file_name = os.path.split(texture_file_name)[-1]
                local_path = os.path.join("objects", file_name)
                image = pyglet.image.load(local_path)
            self.texture = image.get_texture()
            self.textures[texture_file_name] = self.texture
            assert self._value_is_a_power_of_two(image.width)
            assert self._value_is_a_power_of_two(image.height)

    def __copy__(self):
        return self.__class__(diffuse=self.diffuse, ambient=self.ambient, specular=self.specular,
                              emissive=self.emissive, shininess=self.shininess,
                              texture_file_name=self.texture_file_name, name=self.name, alpha=self.alpha)

    @staticmethod
    def _value_is_a_power_of_two(value):
        return ((value & (value - 1)) == 0) and value != 0

    def set_material(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        gl.glTexParameterf(GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameterf(GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        super(OpenGLTexturedMaterial, self).set_material()


class OpenGLWaveFrontParser(ObjectParser):
    def __init__(self):
        super().__init__(object_class=OpenGLMesh, face_class=OpenGLFace, textured_face_class=OpenGLTexturedFace,
                         material_class=OpenGLMaterial, textured_material_class=OpenGLTexturedMaterial)

class OpenGLWaveFrontFactory(WavefrontObjectFactory):

    def __init__(self, files_to_load: List[str]):
        super().__init__(files_to_load, object_parser_class=OpenGLWaveFrontParser)
