from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Grid import GridPoint, BreakerPoint, TargetPoint, Grid

import numpy as np


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
    max_height_of_wave = []

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

        self.target_points = [TargetPoint(x=62, y=37, weight=1),
                              TargetPoint(x=60, y=32, weight=0.5),
                              TargetPoint(x=57, y=18, weight=0.25)]

        self.base_grid = Grid(grid_x=84,
                              grid_y=59,
                              spatial_step=25)

        self.model_grid = self.base_grid

        self.base_breakers = [breaker for breaker in all_base_breakers if
                              (breaker.breaker_id in ['Ia', 'Ib', 'II', 'IIIa', 'IIIb'])]

        self.wind_direction = 135
        self.wind_enabled = True

        self.max_height_of_wave = 80

        self.fairways = [Fairway(GridPoint(20, 20), GridPoint(30, 28), importance=0.5),
                         Fairway(GridPoint(30, 28), GridPoint(60, 22), importance=0.3),
                         Fairway(GridPoint(60, 22), GridPoint(67, 27), importance=0.7),
                         # internal
                         Fairway(GridPoint(50, 24), GridPoint(51, 30), importance=1),
                         Fairway(GridPoint(51, 30), GridPoint(71, 49), importance=0.7),
                         Fairway(GridPoint(71, 49), GridPoint(71, 55), importance=0.7)]

