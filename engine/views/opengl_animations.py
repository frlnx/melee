from .opengl_mesh import OpenGLFace


def explode(face: OpenGLFace, dt: float):
    face.rotate(dt * 90, dt * 90, dt * 90)
    face.translate(*(a * 3 * dt for a in face._original_position))
