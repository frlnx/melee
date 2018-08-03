from collections import defaultdict
from itertools import product, chain

from engine.models import BaseModel


class SpacialIndex(object):
    
    def __init__(self):
        self._2d_space_index: defaultdict[tuple, set] = defaultdict(set)
        self._model_quadrant_index: defaultdict[BaseModel, set] = defaultdict(set)
    
    def other_models(self, model: BaseModel) -> set:
        s = self.all_models(self._model_quadrant_index[model])
        try:
            s.remove(model)
        except KeyError:
            print(s)
        return s

    def all_models(self, quadrants):
        s = set()
        for q in quadrants:
            s = s | self._2d_space_index[q]
        return s

    def all_pairs_deduplicated(self, models):
        pairs = set(chain(*[product([model], self.other_models(model)) for model in models]))
        duplicates = set()
        for pair in pairs:
            if (pair[1], pair[0]) in pairs and (pair[1], pair[0]) not in duplicates:
                duplicates.add(pair)
        return pairs - duplicates

    def init_model_into_2d_space_index(self, model: BaseModel):
        current_quadrants = model.bounding_box.quadrants
        for q in current_quadrants:
            self._add_model_to_2d_space_index(model, q)

    def clear_model_from_2d_space_index(self, model: BaseModel):
        print(f'clearing {model}')
        current_quadrants = model.bounding_box.quadrants
        for q in current_quadrants:
            self._remove_model_from_2d_space_index(model, q)

    def reindex_spacial_position(self, model: BaseModel):
        last_quadrants = self._model_quadrant_index[model]
        current_quadrants = model.bounding_box.quadrants
        removed_quadrants = last_quadrants - current_quadrants
        new_quadrants = current_quadrants - last_quadrants
        for q in removed_quadrants:
            self._remove_model_from_2d_space_index(model, q)
        for q in new_quadrants:
            self._add_model_to_2d_space_index(model, q)

    def _remove_model_from_2d_space_index(self, model: BaseModel, index: tuple):
        self._2d_space_index[index].remove(model)
        self._model_quadrant_index[model].remove(index)

    def _add_model_to_2d_space_index(self, model: BaseModel, index: tuple):
        self._2d_space_index[index].add(model)
        self._model_quadrant_index[model].add(index)
