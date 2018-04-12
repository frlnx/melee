import pyglet
from pyglet.gl import *

#glEnable(GL_TEXTURE_2D)
image = pyglet.image.load("objects/ROCKS001.TGA")
texture = image.get_texture()

window = pyglet.window.Window()

@window.event
def on_draw():
    window.clear()
    glEnable(texture.target)
    glBindTexture (GL_TEXTURE_2D, texture.id)
    glBegin (GL_QUADS)
    glTexCoord2i (0, 0)
    glVertex2i (0, 0)
    glTexCoord2i (1, 0)
    glVertex2i (100, 0)
    glTexCoord2i (1, 1)
    glVertex2i (100, 100)
    glTexCoord2i (0, 1)
    glVertex2i (0, 100)
    glEnd ()

if __name__ == "__main__":
    pyglet.app.run()
