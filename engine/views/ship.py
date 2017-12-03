from typing import Set

from engine.models.ship import ShipModel
from engine.views.ship_part import ShipPartView
from engine.views.base_view import BaseView


class ShipView(BaseView):

    def __init__(self, model: ShipModel, sub_views: Set[ShipPartView]):
        super().__init__(model, sub_views)
