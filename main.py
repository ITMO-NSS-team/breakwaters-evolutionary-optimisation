from Classes.Breaker import Breaker_descr, xy_to_points, Breaker
from Classes.Obstacler import Obstacler
from Classes.Harbor import SochiHarbor
from Classes.WaveModel import SimpleGeomWaveModel, WaveSimulationResult

exp_domain = SochiHarbor()

all_modifications = []

all_modifications = {
    "mod1": Breaker_descr(list(map(xy_to_points, [[30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
    "mod2": Breaker_descr(list(map(xy_to_points, [[24, 16], [33, 22], [42, 17]])), 0, 'Ia'),
    "mod12": Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
    "mod26": Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),
}

breaker_modification_1 = Breaker("mod1", all_modifications["mod1"])
breaker_modification_12 = Breaker("mod12", all_modifications["mod12"])
breaker_modification_26 = Breaker("mod26", all_modifications["mod26"])

modifications = [breaker_modification_1, breaker_modification_12, breaker_modification_26]

fake_obstacler = Obstacler(exp_domain.model_grid, index_mode=True)

construction_indexes = fake_obstacler.get_obstacle_for_modification(exp_domain.base_breakers, modifications)

wave_model = SimpleGeomWaveModel(exp_domain)
simulation_result = wave_model.run_simulation_for_constructions(construction_indexes)

hs0 = simulation_result.get_hs_for_target_point(exp_domain.target_points[0])

print(hs0)