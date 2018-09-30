from engine.models.ship_parts import *
from engine.views.factories import DynamicViewFactory
from engine.views.ship import *
from .base import ShipPartDrydockView, ShipPartConfigurationView, NewPartDrydockView
from .thruster_view import ThrusterDrydockView


class DrydockViewFactory(DynamicViewFactory):

    def __init__(self):
        self.model_view_map = {
            ThrusterModel: ThrusterDrydockView,
            ShipModel: ShipBuildView
        }
        super().__init__(default_sub_view_class=ShipPartDrydockView, default_view_class=ShipBuildView)


class ConfigViewFactory(DynamicViewFactory):

    def __init__(self):
        super().__init__(default_sub_view_class=ShipPartConfigurationView, default_view_class=ShipView)


class PartStoreViewFactory(DynamicViewFactory):

    def __init__(self):
        self.model_view_map = {}
        super().__init__(default_sub_view_class=NewPartDrydockView, default_view_class=NewPartDrydockView)
