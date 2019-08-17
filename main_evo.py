from Configuration.Domains import SochiHarbor
from Simulation.WaveModel import SimpleGeomWaveModel
from Optimisation.Optimiser import ManualOptimiser, StubOptimiser, DifferentialEvolutionaryOptimiser
from Breakers.Breaker import xy_to_points, Breaker

from Optimisation.Objectives import CostObjective, NavigationObjective, WaveHeightObjective
from Optimisation.OptimisationTask import OptimisationTask

exp_domain = SochiHarbor()

wave_model = SimpleGeomWaveModel(exp_domain)

optimiser = DifferentialEvolutionaryOptimiser()

# base_modifications_for_tuning_predef = {
#    'mod1': Breaker_descr(list(map(xy_to_points, [[30, 20], [30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
#    'mod2_top': Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
#    'mod2_bottom': Breaker_descr(list(map(xy_to_points, [[50, 32], [50, 39], [53, 40]])), 0, 'II'),
#    'mod3a': Breaker_descr(list(map(xy_to_points, [[67, 35], [56, 32], [54, 31]])), 0, 'IIIa'),
#    'mod3b': Breaker_descr(list(map(xy_to_points, [[67, 39], [63, 38], [63, 40], [65, 41]])), 0, 'IIIb'),
#    'mod_add': Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),
# }

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 39]])), 0, 'II'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 39], [53, 40]])), 0, 'II'),
    Breaker('mod3a', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 32], [54, 31]])), 0.9, 'IIIa'),
    Breaker('mod3b', list(map(xy_to_points, [[-1, -1], [-1, -1], [63, 38], [63, 40], [65, 41]])), 0.9, 'IIIb'),
    Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 38]])), 0.9, '-'),
]

mod_points_to_optimise = {
    'mod1': [0, 1],
    'mod2_top': [0, 1],
    'mod2_bottom': [0, 1],
    'mod3a': [0, 1],
    'mod3b': [0, 1],
    'mod_add': [0, 1],
}

selected_modifications_for_tuning = base_modifications_for_tuning
selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

constraints = [CostObjective(), NavigationObjective(), WaveHeightObjective()]

task = OptimisationTask(constraints, selected_modifications_for_tuning, mod_points_to_optimise,)

opt_result = optimiser.optimise(wave_model, task)

hs0 = opt_result.simulation_result.get_output_for_target_points(exp_domain.target_points[0])

print(hs0)
