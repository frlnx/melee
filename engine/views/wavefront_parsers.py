from typing import List, Tuple
from os import path
from math import cos, sin, radians


class Face(object):

    def __init__(self, vertices: list, normals: list, material: 'Material'):
        self._vertices = vertices
        self._original_vertices = vertices.copy()
        self._normals = normals
        self.material = material
        self.n_vertices = len(self._vertices)
        self._observers = set()
        self.center_point = self._calculate_center_point()
        self._original_position = self.center_point

    def _calculate_center_point(self) -> tuple:
        cx = 0
        cy = 0
        cz = 0
        for (x, y, z) in self._vertices:
            cx += x
            cy += y
            cz += z
        cx /= self.n_vertices
        cy /= self.n_vertices
        cz /= self.n_vertices
        return cx, cy, cz

    def __copy__(self):
        return self.__class__(vertices=list(self._vertices), normals=list(self._normals),
                              material=self.material.__copy__())

    def translate(self, *xyz):
        for i in range(self.n_vertices):
            self._vertices[i] = tuple(a + b for a, b in zip(self._vertices[i], xyz))
        self.center_point = tuple(a + b for a, b in zip(self.center_point, xyz))
        self.callback()

    def rotate(self, *pyr):
        (pc, ps), (yc, ys), (rc, rs) = [(cos(radians(v)), sin(radians(v))) for v in pyr]
        for i in range(self.n_vertices):
            x, y, z = (a - b for a, b in zip(self._vertices[i], self.center_point))
            y = pc * y + ps * z
            z = -ps * y + pc * z
            x = yc * x - ys * z
            z = ys * x + ys * z
            x = rc * x + rs * y
            y = -rs * x + rc * y
            self._vertices[i] = tuple(a + b for a, b in zip((x, y, z), self.center_point))
        self.callback()

    def observe(self, callback):
        self._observers.add(callback)

    def unobserve(self, callback):
        try:
            self._observers.remove(callback)
        except KeyError:
            pass

    def callback(self):
        self.center_point = self._calculate_center_point()
        for observer in self._observers:
            observer()


class TexturedFace(Face):

    def __init__(self, vertices: list, texture_coords: list, normals: list, material: 'TexturedMaterial'):
        super().__init__(vertices, normals, material)
        self._texture_coords = texture_coords

    def __copy__(self):
        return self.__class__(vertices=list(self._vertices), normals=list(self._normals),
                              material=self.material.__copy__(), texture_coords=list(self._texture_coords))


class Material(object):

    def __init__(self, diffuse: Tuple[float, float, float], ambient: Tuple[float, float, float],
                 specular: Tuple[float, float, float], emissive: Tuple[float, float, float],
                 shininess: float, name: str, alpha: float=1.0):
        self.name = name
        self.diffuse = diffuse
        self.ambient = ambient
        self.specular = specular
        self.emissive = emissive
        self.shininess = shininess
        self.alpha = alpha



class TexturedMaterial(Material):

    def __init__(self, diffuse: Tuple[float, float, float], ambient: Tuple[float, float, float],
                 specular: Tuple[float, float, float], emissive: Tuple[float, float, float], shininess: float,
                 texture_file_name: str, name: str, alpha: float):
        super().__init__(diffuse, ambient, specular, emissive, shininess, name, alpha)
        self.texture_file_name = texture_file_name



class WaveFrontObject(object):

    def __init__(self, faces: List[Face], textured_faces: List[TexturedFace], name=None, group=None):
        self._faces = faces
        self._textured_faces = textured_faces
        self.name = name
        self.group = group


class MaterialFactory(object):

    def __init__(self, material_class=Material, textured_material_class=TexturedMaterial):
        self._material_class = material_class
        self._textured_material_class = textured_material_class
        self.material_files = {}
        self.material_parser = MaterialParser()

    def load_materials(self, file_name):
        if not file_name in self.material_files:
            with open(path.join("objects", file_name), 'r') as f:
                file_data = f.readlines()
            self.material_files[file_name] = self.material_parser.parse(file_data)

    def manufacture(self, material_file, material_name) -> Material:
        data = self.material_files[material_file][material_name]
        if 'texture_file_name' in data:
            material = self._textured_material_class(**data)
        else:
            material = self._material_class(**data)
        return material


class MaterialParser(object):

    def __init__(self):
        self._material_data = {}
        self._materials = {}
        self.parser_map = {
            "newmtl": self.new_material,
            "Kd": lambda x: ("diffuse", list(map(float, x.split(" ")))),
            "Ke": lambda x: ("emissive", list(map(float, x.split(" ")))),
            "Ka": lambda x: ("ambient", list(map(float, x.split(" ")))),
            "Ks": lambda x: ("specular", list(map(float, x.split(" ")))),
            "Ns": lambda x: ("shininess", float(x)),
            "d": lambda x: ("alpha", float(x)),
            "map_Kd": lambda x: ("texture_file_name", x),
        }

    def parse(self, lines):
        self._material_data = {}
        self._materials = {}
        for line in lines:
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            self._parse_line(line)
        return self._materials

    def _parse_line(self, line: str):
        instruction, data = line.split(' ', 1)
        try:
            func = self.parser_map[instruction]
        except KeyError:
            pass
            #print("Don't know how to interpret instruction {}".format(instruction))
        else:
            key, value = func(data)
            self._material_data[key] = value


    def new_material(self, name):
        self._material_data = {}
        self._materials[name] = self._material_data
        return ("name", name)


class ObjectParser(object):

    def __init__(self, object_class=WaveFrontObject, face_class=Face, textured_face_class=TexturedFace,
                 material_class=Material, textured_material_class=TexturedMaterial):
        self._object_class = object_class
        self._face_class = face_class
        self._textured_face_class = textured_face_class
        self._textured_material_class = textured_material_class
        self._faces = []
        self._textured_faces = []
        self._vertices = []
        self._normals = []
        self.name = None
        self.group = None
        self.smoothing_group = None
        self._vertex_texture_coordinates = []
        self._material_factory = MaterialFactory(material_class, textured_material_class)
        self._current_material_file_name = ""
        self.parser_map = {
            "g": self.set_group,
            "s": self.set_smoothing_group,
            "o": lambda x: self.set_name(x[:-4]),
            "v": lambda x: self.add_vertex(*map(float, x.split(" "))),
            "vn": lambda x: self.add_normal(*map(float, x.split(" "))),
            "vt": lambda x: self.add_texture_coordinate(*map(float, x.split(" "))),
            "f": lambda x: self.add_face(*x.split(" ")),
            "usemtl": self.set_current_material,
            "mtllib": self.load_materials_into_material_factory
        }

    def parse(self, file_lines: List[str]):
        for line in file_lines:
            line = line.strip()
            if line[0] == "#":
                continue
            self._parse_line(line)
        wfo = self._object_class(self._faces, self._textured_faces, name=self.name)
        self._faces = []
        self._textured_faces = []
        self._vertices = []
        self._normals = []
        self._vertex_texture_coordinates = []
        return wfo

    def _parse_line(self, line: str):
        instruction, data = line.split(' ', 1)
        func = self.parser_map.get(instruction, lambda x: print(line))
        func(data)

    def set_group(self, group):
        self.group = group

    def set_smoothing_group(self, smoothing_group):
        self.smoothing_group = smoothing_group

    def set_name(self, name: str):
        assert isinstance(name, str)
        self.name = name

    def add_vertex(self, *xyz):
        self._vertices.append(xyz)

    def add_normal(self, *xyz):
        self._normals.append(xyz)

    def add_texture_coordinate(self, *xy):
        self._vertex_texture_coordinates.append(xy)

    def set_current_material(self, name):
        self._current_material = self._material_factory.manufacture(self._current_material_file_name, name)

    def load_materials_into_material_factory(self, file_name):
        self._current_material_file_name = file_name
        self._material_factory.load_materials(file_name)

    def add_face(self, *data):
        vertices = []
        texture_coords = []
        normals = []
        for vertices_texture_normal in data:
            vertices_id, texture_id, normal_id = vertices_texture_normal.split('/', 2)
            vertices.append(self._vertices[int(vertices_id) - 1])
            if texture_id:
                texture_coords.append(self._vertex_texture_coordinates[int(texture_id) - 1])
            if normal_id:
                normals.append(self._normals[int(normal_id) - 1])
        if isinstance(self._current_material, self._textured_material_class):
            face = self._textured_face_class(vertices, texture_coords, normals, self._current_material)
            self._textured_faces.append(face)
        else:
            face = self._face_class(vertices, normals, self._current_material)
            self._faces.append(face)


class WavefrontObjectFactory(object):

    def __init__(self, files_to_load: List[str], object_parser_class=ObjectParser):
        self.object_map = {}
        object_parser = object_parser_class()
        for file_path in files_to_load:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                wfo = object_parser.parse(lines)
                self.object_map[wfo.name] = wfo

    def manufacture(self, name):
        try:
            return self.object_map[name].__copy__()
        except KeyError:
            print(self.object_map.keys())
            raise
