from engine.models.ship_part import ShipPartModel
from engine.physics.force import MutableOffsets, MutableDegrees


class FuelTankModel(ShipPartModel):

    def __init__(self, name, position: MutableOffsets, rotation: MutableDegrees, movement: MutableOffsets,
                 spin: MutableDegrees, acceleration: MutableOffsets, torque: MutableDegrees, bounding_box, **part_spec):
        self._fuel_stored = part_spec.get('fuel_storage')
        self.max_fuel_stored = part_spec.get('fuel_storage')
        super().__init__(name, position, rotation, movement, spin, acceleration, torque, bounding_box, **part_spec)

    @property
    def working(self):
        return self._working and self.fuel_stored > 0

    def drain_fuel(self, amount):
        if self._fuel_stored is None:
            raise AttributeError(f"No fuel stored in a {self.name}")
        self._fuel_stored -= amount
        self._fuel_stored = max(0, self._fuel_stored)
        if self._fuel_stored == 0:
            self.update_working_status()

    @property
    def fuel_stored(self):
        return self._fuel_stored

    def copy(self, **kwargs) -> "FuelTankModel":
        return self.__class__(name=self.name, position=self.position.__copy__(), rotation=self.rotation.__copy__(),
                              movement=self.movement.__copy__(), spin=self.spin.__copy__(),
                              acceleration=self.acceleration.__copy__(), torque=self.torque.__copy__(),
                              bounding_box=self.bounding_box.__copy__(), states=self._states.copy(),
                              keyboard=self.keyboard, mouse=self.mouse.copy(), axis=self.axis, button=self.button,
                              connectability=self._connectability.copy(), mesh_name=self.mesh_name,
                              material_affected=self.material_affected, material_channels=self.material_channels,
                              material_mode=self.material_mode, fuel_storage=self.max_fuel_stored, **kwargs)