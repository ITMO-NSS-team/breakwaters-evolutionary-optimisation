from Breakers.Breaker import Breaker_descr, xy_to_points, Breaker
from Configuration.Grid import Grid


class TargetPoint:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight


class Domain:
    base_breakers = []
    base_grid = [] #grid for indxing
    model_grid = [] #grid for wave model, now the same

    target_points = []

    wind_direction = 135
    wind_enabled = True


class SochiHarbor(Domain):

    def __init__(self):
        all_base_breakers = {
            "Ia": Breaker_descr(list(map(xy_to_points, [[33, 22], [42, 17]])), 0, ''),
            "Ib": Breaker_descr(list(map(xy_to_points, [[42, 17], [59, 17], [72, 25]])), 0.9, ''),
            "II": Breaker_descr(list(map(xy_to_points, [[50, 32], [50, 39]])), 0, ''),
            "IIIa": Breaker_descr(list(map(xy_to_points, [[67, 35], [56, 32]])), 0.9, ''),
            "IIIb": Breaker_descr(list(map(xy_to_points, [[67, 39], [63, 38]])), 0.9, '')
        }

        self.target_points = [TargetPoint(x=62, y=37, weight=1)]

        self.base_grid = Grid(grid_x=84,
                              grid_y=59,
                              spatial_step=25)

        self.model_grid = self.base_grid

        base_breaker_1 = Breaker("Ia", all_base_breakers["Ia"])
        base_breaker_2 = Breaker("Ib", all_base_breakers["Ib"])
        base_breaker_3 = Breaker("II", all_base_breakers["II"])
        base_breaker_4 = Breaker("IIIa", all_base_breakers["IIIa"])
        base_breaker_5 = Breaker("IIIb", all_base_breakers["IIIb"])

        self.base_breakers = [base_breaker_1, base_breaker_2, base_breaker_3, base_breaker_4, base_breaker_5]
