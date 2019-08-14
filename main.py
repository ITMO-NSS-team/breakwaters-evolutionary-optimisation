from Classes.Breaker import Breaker_descr, xy_to_points, Breaker
from Classes.Grid import Grid
from Classes.Obstacler import Obstacler

grid_x = 84
grid_y = 59
grid_step = 25

all_modifications = []
all_base_breakers = {
    "Ia": Breaker_descr(list(map(xy_to_points, [[33, 22], [42, 17]])), 0, ''),  # не протечёт ли?
    "Ib": Breaker_descr(list(map(xy_to_points, [[42, 17], [59, 17], [72, 25]])), 0.9, ''),
    "II": Breaker_descr(list(map(xy_to_points, [[50, 32], [50, 39]])), 0, ''),
    "IIIa": Breaker_descr(list(map(xy_to_points, [[67, 35], [56, 32]])), 0.9, ''),
    "IIIb": Breaker_descr(list(map(xy_to_points, [[67, 39], [63, 38]])), 0.9, '')
}

all_modifications = {
    "mod1": Breaker_descr(list(map(xy_to_points, [[30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
    "mod2": Breaker_descr(list(map(xy_to_points, [[24, 16], [33, 22], [42, 17]])), 0, 'Ia'),
    "mod12": Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
    "mod26": Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),

}

grid = Grid(grid_x=grid_x,
            grid_y=grid_y,
            spatial_step=grid_step)

base_breaker_1 = Breaker("Ia", all_base_breakers["Ia"])
base_breaker_2 = Breaker("Ib", all_base_breakers["Ib"])
base_breaker_3 = Breaker("II", all_base_breakers["II"])
base_breaker_4 = Breaker("IIIa", all_base_breakers["IIIa"])
base_breaker_5 = Breaker("IIIb", all_base_breakers["IIIb"])

base_breakers = [base_breaker_1, base_breaker_2, base_breaker_3, base_breaker_4, base_breaker_5]

breaker_modification_1 = Breaker("mod1", all_modifications["mod1"])
breaker_modification_12 = Breaker("mod12", all_modifications["mod12"])
breaker_modification_26 = Breaker("mod26", all_modifications["mod26"])

modifications = [breaker_modification_1, breaker_modification_12, breaker_modification_26]

fake_obstacler = Obstacler(grid, index_mode=True)

obstacle_items = fake_obstacler.get_obstacle_for_modification(base_breakers, modifications)

for obst_item in obstacle_items:
    print(obst_item)
