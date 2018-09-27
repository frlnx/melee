from itertools import chain

from pyglet.gl import GL_LINES
from pyglet.graphics import draw

from engine.models.ship_parts import ThrusterModel
from engine.views.ship_part import ShipPartDrydockView


class ThrusterDrydockView(ShipPartDrydockView):

    def __init__(self, model: ThrusterModel, mesh):
        super().__init__(model, mesh)
        #self.model = model
        self.angles_v3f = []
        self.update_angles()
        model._center_of_mass.observe(self.update_angles)

    def update(self):
        super(ThrusterDrydockView, self).update()
        self.update_angles()

    def update_angles(self):
        direction = self.model.position - self.model.rotation.direction
        #full_torque_degrees = int(self.model.full_torque)
        #slices = max(int(sqrt(full_torque_degrees)), 2)
        #degrees_per_slice = int(full_torque_degrees / slices)
        #for i in range(0, full_torque_degrees, degrees_per_slice):

        self.angles_v3f = list(chain(self.model.position,
                                     self.model.center_of_mass,
                                     self.model.position,
                                     direction))

    def _draw_global(self):
        super(ThrusterDrydockView, self)._draw_global()
        draw(4, GL_LINES, ('v3f', self.angles_v3f))
