from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Grid import *


class GridPoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class TargetPoint(GridPoint):
    def __init__(self, x, y, weight):
        super(TargetPoint, self).__init__(x, y)
        self.weight = weight


class Fairway:
    def __init__(self, p1: GridPoint, p2: GridPoint, importance):
        self.x1 = p1.x
        self.y1 = p1.y
        self.x2 = p2.x
        self.y2 = p2.y
        self.importance = importance
        assert self.importance <= 1


class Domain:
    base_breakers = []
    base_grid = []  # grid for indxing
    model_grid = []  # grid for wave model, now the same

    target_points = []

    wind_direction = []
    wind_enabled = True

    fairways = []


class SochiHarbor(Domain):

    def __init__(self):
        all_base_breakers = [
            Breaker('Ia', list(map(xy_to_points, [[33, 22], [42, 17]])), 0, ''),
            Breaker('Ib', list(map(xy_to_points, [[42, 17], [59, 17], [72, 25]])), 0.9, ''),
            Breaker('II', list(map(xy_to_points, [[50, 32], [50, 39]])), 0, ''),
            Breaker('IIIa', list(map(xy_to_points, [[67, 35], [56, 32]])), 0.9, ''),
            Breaker('IIIb', list(map(xy_to_points, [[67, 39], [63, 38]])), 0.9, '')
        ]

        self.target_points = [TargetPoint(x=62, y=37, weight=1)]

        self.base_grid = Grid(grid_x=84,
                              grid_y=59,
                              spatial_step=25)

        self.model_grid = self.base_grid

        self.base_breakers = [breaker for breaker in all_base_breakers if
                              (breaker.breaker_id in ['Ia', 'Ib', 'II', 'IIIa', 'IIIb'])]

        self.wind_direction = 135
        self.wind_enabled = True

        self.fairways = [Fairway(GridPoint(20, 30), GridPoint(60, 25), 1)]  # TODO fill with real coordinates
