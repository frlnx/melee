from engine.models.observable import Observable


class PositionalModel(Observable):

    def __init__(self, x, y, z, pitch, yaw, roll, breadth_scale, height_scale, depth_scale):
        super().__init__()
        self._x, self._y, self._z, self._pitch, self._yaw, self._roll = x, y, z, pitch, yaw, roll
        self._breadth_scale, self._height_scale, self._depth_scale = breadth_scale, height_scale, depth_scale

    @property
    def position(self):
        return self._x, self._y, self._z

    @property
    def x(self):
        return self.x

    @property
    def y(self):
        return self.y

    @property
    def z(self):
        return self.z

    @property
    def rotation(self):
        return self._pitch, self._yaw, self._roll

    @property
    def pitch(self):
        return self.pitch

    @property
    def yaw(self):
        return self.yaw

    @property
    def roll(self):
        return self.roll

    @property
    def scale(self):
        return self._breadth_scale, self._height_scale, self._depth_scale

    @property
    def breadth_scale(self):
        return self._breadth_scale

    @property
    def height_scale(self):
        return self._height_scale

    @property
    def depth_scale(self):
        return self._depth_scale
