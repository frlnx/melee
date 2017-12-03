from engine.models.base_model import BaseModel
from engine.views.base_view import BaseView


class ViewFactory(object):

    def __init__(self):
        pass

    def manufacture(self, model: BaseModel) -> BaseView:
        ship_view = BaseView(model)
        return ship_view
