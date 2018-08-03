from functools import partial
from random import random

from .opengl_mesh import OpenGLFace


class Explosion(object):

    def __init__(self, faces: list):
        self.animators = [partial(self.explode, face, random(), random(), random(), random()) for face in faces]

    @staticmethod
    def explode(face: OpenGLFace, pitch, yaw, roll, speed, dt: float):
        face.rotate(dt * pitch * 180, dt * yaw * 180, dt * roll * 180)
        face.translate(*(a * speed * 6 * dt for a in face._original_position))

    def animate(self, dt):
        for animator in self.animators:
            animator(dt)

    def expire(self):
        self.animators = []
