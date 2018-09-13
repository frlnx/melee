from .base_model import BaseModel


class AsteroidModel(BaseModel):

    destructable = False

    @property
    def mass(self):
        return 100000000
