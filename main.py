from Configuration.Domains import SochiHarbor
from Simulation.WaveModel import SimpleGeomWaveModel
from Optimisation.Optimiser import ManualOptimiser, StubOptimiser
from Breakers.Breaker import Breaker_descr, xy_to_points, Breaker

exp_domain = SochiHarbor()

wave_model = SimpleGeomWaveModel(exp_domain)

optimiser = StubOptimiser()

manual_modifications = {
    'mod1': Breaker_descr(list(map(xy_to_points, [[30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
    'mod2': Breaker_descr(list(map(xy_to_points, [[24, 16], [33, 22], [42, 17]])), 0, 'Ia'),
    'mod12': Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
    'mod26': Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),
}

opt_result = optimiser.optimise(wave_model, manual_modifications, [])

hs0 = opt_result.simulation_result.get_output_for_target_point(exp_domain.target_points[0])

print(hs0)
