from typing import Dict, Tuple

from pywavefront import Wavefront
from pyglet.graphics import glTranslatef, glRotatef, glPushMatrix, glPopMatrix

FILE_TEMPLATE = "objects/{}.obj"


class ShipPart(object):

    def __init__(self, name, position: list, rotation=0, **_):
        self.name = name
        self.position = position
        self.pitch = 0
        self.yaw = rotation
        self.roll = 0
        self.mesh = Wavefront(FILE_TEMPLATE.format(name))

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(self.roll, 0, 0, 1)
        self.mesh.draw()
        glPopMatrix()


class Ship(object):

    def __init__(self, parts: Dict[Tuple[int, int], ShipPart]):
        self.parts = parts
        self.position = [0, 0, 0]
        self.pitch = 0
        self.yaw = 0
        self.roll = 0

    def draw(self):
        glPushMatrix()
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        glRotatef(self.roll, 0, 0, 1)
        glTranslatef(*self.position)
        for part in self.parts.values():
            part.draw()
        glPopMatrix()
