from engine.models.base_model import BaseModel


class PlasmaModel(BaseModel):

    @property
    def mesh(self):
        return "plasma"
