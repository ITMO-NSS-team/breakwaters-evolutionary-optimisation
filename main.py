from Breakers.Breaker import Breaker_descr, xy_to_points, Breaker
from Breakers.Obstacler import Obstacler
from Configuration.Harbor import SochiHarbor
from Simulation.WaveModel import SimpleGeomWaveModel

exp_domain = SochiHarbor()

manual_modifications = []

manual_modifications = {
    "mod1": Breaker_descr(list(map(xy_to_points, [[30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
    "mod2": Breaker_descr(list(map(xy_to_points, [[24, 16], [33, 22], [42, 17]])), 0, 'Ia'),
    "mod12": Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
    "mod26": Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),
}

modifications = [Breaker(_, manual_modifications[_]) for _ in ["mod1", "mod12", "mod26"]]

fake_obstacler = Obstacler(exp_domain.model_grid, index_mode=True)

construction_indexes = fake_obstacler.get_obstacle_for_modification(exp_domain.base_breakers, modifications)

wave_model = SimpleGeomWaveModel(exp_domain)
simulation_result = wave_model.run_simulation_for_constructions(construction_indexes)

hs0 = simulation_result.get_output_for_target_point(exp_domain.target_points[0])

print(hs0)
