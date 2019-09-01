from Configuration.Domains import SochiHarbor
from Simulation.WaveModel import SimpleGeomWaveModel, SwanWaveModel
from Optimisation.Optimiser import ManualOptimiser, StubOptimiser, DifferentialEvolutionaryOptimiser, \
    ParetoEvolutionaryOptimiser
from Breakers.Breaker import xy_to_points, Breaker

from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
import random
import numpy as np



np.random.seed(42)
random.seed(42)

exp_domain = SochiHarbor()

wave_model = SimpleGeomWaveModel(exp_domain)

optimiser = ParetoEvolutionaryOptimiser()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 39]])), 0, 'II'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 39]])), 0, 'II'),
    Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa'),
    Breaker('mod3short', list(map(xy_to_points, [[-1, -1], [-1, -1], [63, 38], [67, 39]])), 0.9, 'IIIb'),
    Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 42]])), 0.9, '-'),
]

mod_points_to_optimise = {  # order is important
    'mod1': [1, 0],
    'mod2_top': [1, 0],
    'mod2_bottom': [1, 0],
    'mod3long': [1, 0],
    'mod3short': [1, 0],
    'mod_add': [1, 0],
}

selected_modifications_for_tuning = base_modifications_for_tuning
selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

objectives = [  # StructuralObjective(importance=1),
    CostObjective(importance=3),
    # NavigationObjective(importance=1),
    WaveHeightObjective(importance=2)]

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

opt_result = optimiser.optimise(wave_model, task)
