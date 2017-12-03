from engine.models.ship import ShipModel
from engine.views.ship import ShipView
from engine.views.ship_part import ShipPartView

class ShipViewFactory(object):

    def __init__(self):
        pass

    def manufacture(self, model: ShipModel) -> ShipView:
        sub_views = set(ShipPartView(ship_part_model) for ship_part_model in model.parts)
        ship_view = ShipView(model, sub_views)
        return ship_view
