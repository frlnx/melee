from engine.models.ship_part import ShipPartModel


class ShieldModel(ShipPartModel):

    def run(self, dt):
        charge = self.input_value * self.state_spec.get('shield_charge_amount', 0)
        self._callback("load_charge", amount=charge * dt)