from .opengl_mesh import OpenGLMaterial


def extinguish(material: OpenGLMaterial, dt):
    ambient = (max(0, round(ma * 0.9 * dt, 3)) for ma in material.ambient)
    material.update(ambient=ambient)
