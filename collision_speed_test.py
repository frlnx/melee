from itertools import combinations
from math import pi
from random import normalvariate, random

from engine.physics.polygon import MultiPolygon, PolygonPart


def make_multipolygon(x, y, r):
    coords = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    polygons = [PolygonPart.manufacture(coords, x=px, y=py) for px, py in coords]
    target = MultiPolygon(polygons)
    target.set_position_rotation(x, y, r)
    target.clear_movement()
    target.set_position_rotation(x+1, y+1, r+0.5)
    return target


def setup():
    polygons = [make_multipolygon(normalvariate(100, 20), normalvariate(100, 20), random() * pi * 2) for i in range(10)]
    return polygons


def statement(polygons):
    for p1, p2 in combinations(polygons, 2):
        p1.intersected_polygons(p2)


if __name__ == '__main__':
    import timeit
    t = timeit.Timer("statement(polygons)", setup="from __main__ import setup, statement; polygons=setup()")
    results = t.repeat(number=100, repeat=10)
    print("\n".join(str(f) for f in results))
    print("AVG:", sum(results) / len(results))
    nineteyfive_five = set(results)
    nineteyfive_five.remove(max(results))
    nineteyfive_five.remove(min(results))
    print("95-5:", sum(nineteyfive_five) / len(nineteyfive_five))
