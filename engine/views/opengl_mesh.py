from pyglet.gl import *
import pyglet
from ctypes import c_float
from functools import partial
from itertools import chain
from collections import defaultdict
from typing import List, Tuple
import os

from engine.views.wavefront_parsers import WaveFrontObject, Face, TexturedFace, Material
from engine.views.wavefront_parsers import ObjectParser, WavefrontObjectFactory


class Drawable(object):
    __abstract__ = True

    def draw(self):
        pass

    def set_double_sided(self, state):
        if state:
            self._configure_cull_face = self._disable_cull_face
        else:
            self._configure_cull_face = self._enable_cull_face

    def _configure_cull_face(self):
        pass

    def _enable_cull_face(self):
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

    def _disable_cull_face(self):
        glDisable(GL_CULL_FACE)


class OpenGLMesh(WaveFrontObject):

    def __init__(self, faces: List['OpenGLFace'], textured_faces: List['OpenGLTexturedFace'], name=None, group=None):
        super().__init__(faces, textured_faces, name, group)
        self.materials = {face.material.name: face.material for face in chain(faces, textured_faces)}
        self.drawables = self._render_bundles()
        self.animations = set()
        self.transmutations = set()

    def update_material(self, material_name, material_mode, material_channel, value):
        channels = 'rgba'
        values = [int(channel not in material_channel) or value for channel in channels]
        self.materials[material_name].update(**{material_mode: values})

    def __copy__(self):
        faces = [face.__copy__() for face in self._faces]
        textured_faces = [face.__copy__() for face in self._textured_faces]
        materials = {material.name: material.__copy__() for material in self.materials.values()}
        for face in chain(faces, textured_faces):
            face.material = materials[face.material.name]
        copy = self.__class__(faces, textured_faces, name=self.name, group=self.group)
        return copy

    def _render_bundles(self):
        faces_by_material_n_points_draw_mode = defaultdict(list)
        for face in self._faces + self._textured_faces:
            n_points = min(face.n_vertices, 5)
            material_n_points_draw_mode_key = (face.material.name, n_points, face.draw_mode)
            faces_by_material_n_points_draw_mode[material_n_points_draw_mode_key].append(face)
        bundles = set()
        for (material_name, n_points, draw_mode), faces in faces_by_material_n_points_draw_mode.items():
            material = self.materials[material_name]
            bundle = OpenGLFaceBundle(faces, material, n_points, draw_mode)
            bundles.add(bundle)
        return bundles

    def set_double_sided(self, state):
        for drawable in self.drawables:
            drawable.set_double_sided(state)

    def add_transmutation(self, transmutation):
        self.transmutations.add(transmutation)

    def remove_transmutation(self, transmutation):
        try:
            self.transmutations.remove(transmutation)
        except KeyError:
            pass

    def add_animation(self, animation):
        self.animations.add(animation)

    def remove_animation(self, animation):
        try:
            self.animations.remove(animation)
        except KeyError:
            pass

    def timer(self, dt):
        for animation in self.animations:
            for face in self._faces + self._textured_faces:
                animation(face, dt)
        for transmutation in self.transmutations:
            for material in self.materials.values():
                transmutation(material, dt)

    def add_drawable(self, drawable):
        self.drawables.add(drawable)

    def remove_drawable(self, drawable):
        try:
            self.drawables.remove(drawable)
        except KeyError:
            pass

    def draw(self):
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT | GL_LIGHTING_BIT)
        glDisable(GL_TEXTURE_2D)
        for bundle in self.drawables:
            bundle.draw()
        glPopAttrib()
        glPopClientAttrib()

    def __repr__(self):
        return f'Mesh {self.name}'


class OpenGLFace(Face):
    draw_mode = GL_N3F_V3F

    def __init__(self, vertices: list, normals: list, material: 'OpenGLMaterial'):
        super().__init__(vertices, normals, material)
        self.draw_data = self._n3f_v3f()
        self.n_vertices = len(self._vertices)

    def get_draw_data(self):
        return self._n3f_v3f()

    def _n3f_v3f(self):
        n3f_v3f = []
        for n, v in zip(self._normals, self._vertices):
            n3f_v3f += n
            n3f_v3f += v
        return n3f_v3f


class OpenGLTexturedFace(TexturedFace):
    draw_mode = GL_T2F_N3F_V3F

    def __init__(self, vertices: list, texture_coords: list, normals: list, material: 'OpenGLTexturedMaterial'):
        super().__init__(vertices, texture_coords, normals, material)
        self.draw_data = self._t2f_n3f_v3f()

    def get_draw_data(self):
        return self._t2f_n3f_v3f()

    def _t2f_n3f_v3f(self):
        t2f_n3f_v3f = []
        for n, t, v in zip(self._normals, self._texture_coords, self._vertices):
            t2f_n3f_v3f += t
            t2f_n3f_v3f += n
            t2f_n3f_v3f += v
        return t2f_n3f_v3f


class OpenGLMaterial(Material):
    def __init__(self, diffuse: Tuple[float, float, float] = None, ambient: Tuple[float, float, float] = None,
                 specular: Tuple[float, float, float] = None, emissive: Tuple[float, float, float] = None,
                 shininess: float = 0.0, name: str = None, alpha: float = 1.0):
        diffuse = diffuse or (0, 0, 0)
        ambient = ambient or (0, 0, 0)
        specular = specular or (0, 0, 0)
        emissive = emissive or (0, 0, 0)
        name = name or "Unnamed Material"
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
        ones = (1, 1, 1, kwargs.get('alpha', 1))
        opengl_diffuse = [a * b for a, b in zip(kwargs.get('diffuse', ones), self.original_opengl_diffuse)]
        self.opengl_diffuse = self.to_c_arr(opengl_diffuse)
        self.opengl_ambient = self.to_c_arr((a * b for a, b in zip(kwargs.get('ambient', ones), self.original_opengl_ambient)))
        self.opengl_specular = self.to_c_arr((a * b for a, b in zip(kwargs.get('specular', ones), self.original_opengl_specular)))
        self.opengl_emissive = self.to_c_arr((a * b for a, b in zip(kwargs.get('emissive', ones), self.original_opengl_emissive)))
        self.opengl_shininess = (kwargs.get('shininess', self.original_opengl_shininess) / 1000) * 128

    def __copy__(self):
        return self.__class__(diffuse=self.diffuse, ambient=self.ambient, specular=self.specular,
                              emissive=self.emissive, shininess=self.shininess, name=self.name, alpha=self.alpha)

    def __getstate__(self):
        d = {}
        for k, val in self.__dict__.items():
            if 'opengl' in k and 'opengl_shininess' not in k:
                d[k] = list(val)
            else:
                d[k] = val
        return d

    def __setstate__(self, state):
        d = {}
        for k, val in state.items():
            if 'opengl' in k and 'opengl_shininess' not in k:
                d[k] = self.to_c_arr(val)
            else:
                d[k] = val
        self.__dict__.update(d)

    @staticmethod
    def to_c_arr(values) -> List[c_float]:
        c_arr = (c_float * 4)
        return c_arr(*values)

    @staticmethod
    def _revert_from_c_float_arr(values):
        return list(values)

    @staticmethod
    def _convert_zero_to_one_values_into_minus_one_to_one_values(value: float) -> float:
        return value  # * 2 - 1

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

    def __init__(self, texture_file_name: str, diffuse: Tuple[float, float, float] = None,
                 ambient: Tuple[float, float, float] = None, specular: Tuple[float, float, float] = None,
                 emissive: Tuple[float, float, float] = None, shininess: float = 0.0, name: str = None,
                 alpha: float = 1.0):
        super().__init__(diffuse, ambient, specular, emissive, shininess, name, alpha)
        self.texture_file_name = texture_file_name
        self.texture = self.load_texture()

    def load_texture(self):
        try:
            texture = self.textures[self.texture_file_name]
        except:
            try:
                image = pyglet.image.load(self.texture_file_name)
            except FileNotFoundError:
                file_name = os.path.split(self.texture_file_name)[-1]
                local_path = os.path.join("objects", file_name)
                image = pyglet.image.load(local_path)
            texture = image.get_texture()
            self.textures[self.texture_file_name] = texture
            assert self._value_is_a_power_of_two(image.width)
            assert self._value_is_a_power_of_two(image.height)
        return texture

    def __copy__(self):
        return self.__class__(diffuse=self.diffuse, ambient=self.ambient, specular=self.specular,
                              emissive=self.emissive, shininess=self.shininess,
                              texture_file_name=self.texture_file_name, name=self.name, alpha=self.alpha)

    def __getstate__(self):
        d = super(OpenGLTexturedMaterial, self).__getstate__()
        # del d['textures']
        d['texture'] = None
        return d

    def __setstate__(self, state):
        super(OpenGLTexturedMaterial, self).__setstate__(state)
        self.texture = self.load_texture()

    @staticmethod
    def _value_is_a_power_of_two(value):
        return ((value & (value - 1)) == 0) and value != 0

    def set_material(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id)
        gl.glTexParameterf(GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameterf(GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        super(OpenGLTexturedMaterial, self).set_material()


class OpenGLFaceBundle(Drawable):
    shape_by_n_points = {3: GL_TRIANGLES, 4: GL_QUADS}

    def __init__(self, faces: List[OpenGLFace], material=None, n_points=None, draw_mode=None, **config):
        self.faces = faces
        self.material = material or faces[0].material
        self.n_points = n_points or min(faces[0].n_vertices, 5)
        self.draw_mode = draw_mode or faces[0].draw_mode
        self.shape = self.shape_by_n_points[self.n_points]
        self.draw_data = []
        for face in faces:
            face.observe(partial(self._update_c_draw_data, face.get_draw_data, len(self.draw_data)))
            self.draw_data += face.draw_data
        self.data_length = len(self.draw_data)
        self.c_arr = c_float * self.data_length
        self.c_draw_data = self.c_arr(*self.draw_data)
        if config.get('double_sided', False):
            self._configure_cull_face = self._disable_cull_face
        else:
            self._configure_cull_face = self._enable_cull_face

    def _update_c_draw_data(self, data_func, start: int):
        data = data_func()
        end = start + len(data)
        self.c_draw_data[start:end] = data

    def __getstate__(self):
        d = {k: val for k, val in self.__dict__.items()}
        del d['c_arr']
        del d['c_draw_data']
        return d

    def __setstate__(self, state):
        state["c_arr"] = c_float * state['data_length']
        state["c_draw_data"] = state['c_arr'](*state['draw_data'])
        self.__dict__.update(state)

    def draw(self):
        self._configure_cull_face()
        self.material.set_material()
        glInterleavedArrays(self.draw_mode, 0, self.c_draw_data)
        glDrawArrays(self.shape, 0, len(self.faces) * self.n_points)

    def __repr__(self):
        return "{} {}-gons of {}".format(len(self.faces), self.n_points, self.material.name)


class OpenGLWaveFrontParser(ObjectParser):
    def __init__(self, object_class=OpenGLMesh):
        super().__init__(object_class=object_class, face_class=OpenGLFace, textured_face_class=OpenGLTexturedFace,
                         material_class=OpenGLMaterial, textured_material_class=OpenGLTexturedMaterial)


class OpenGLWaveFrontFactory(WavefrontObjectFactory):

    def __init__(self, files_to_load: List[str]):
        super().__init__(files_to_load, object_parser_class=OpenGLWaveFrontParser)
