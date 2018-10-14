from typing import Dict

from pyglet.gl import *
from pyglet.graphics import Batch, vertexdomain
from pyglet.text import Label

from gui.models.container import ComponentContainerModel
from gui.views.container import ContainerView
from gui.views.drawables.drawable import Drawable


class Viewport(ContainerView):

    def __init__(self, model: ComponentContainerModel, batch: Batch=None):
        super().__init__(model)
        self._model = model
        self._batch = batch or Batch()
        self._vertex_lists = set()
        self._vertex_list_by_drawable: Dict[Drawable, vertexdomain.VertexList] = dict()

    def __enter__(self):
        self.setup()

    def setup(self):
        glViewport(self._model.left * 2, self._model.bottom * 2, self._model.width * 2, self._model.height * 2)

    def draw(self):
        self.setup()
        self._batch.draw_subset(self._vertex_lists)

    def add_drawable(self, drawable: Drawable):
        super(Viewport, self).add_drawable(drawable)
        count, mode, group, data = drawable.n_coordinates, drawable.mode, drawable.group, drawable.draw_data
        vertex_list = self._batch.add(count, mode, group, *data)
        self._vertex_lists.add(vertex_list)
        self._vertex_list_by_drawable[drawable] = vertex_list
        drawable.observe(self.recolor_drawable, Drawable.SIGNAL_RECOLOR)
        drawable.observe(self.reposition_drawable, Drawable.SIGNAL_REPOSITION)
        drawable.observe(self.reposition_texture, Drawable.SIGNAL_REPOSITION_TEXTURE)
        drawable.observe(self.renormalize_drawable, Drawable.SIGNAL_RENORMALIZE)

    def add_text(self, text: Label):
        super(Viewport, self).add_text(text)
        text.batch = self._batch
        self._vertex_lists |= set(text._vertex_lists)

    def recolor_drawable(self, caller: Drawable):
        vertex_list = self._vertex_list_by_drawable[caller]
        vertex_list.colors = caller.colors

    def reposition_drawable(self, caller: Drawable):
        vertex_list = self._vertex_list_by_drawable[caller]
        vertex_list.vertices = caller.vertices

    def reposition_texture(self, caller: Drawable):
        vertex_list = self._vertex_list_by_drawable[caller]
        vertex_list.tex_coords = caller.tex_coords

    def renormalize_drawable(self, caller: Drawable):
        vertex_list = self._vertex_list_by_drawable[caller]
        vertex_list.normals = caller.normals


class PerspectiveViewport(Viewport):

    def setup(self):
        super(PerspectiveViewport, self).setup()
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., self._model.aspect_ratio, 1, 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


class OrthoViewport(Viewport):

    def setup(self):
        super(OrthoViewport, self).setup()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(self._model.left, self._model.right, self._model.bottom, self._model.top, -1., 1000.)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
