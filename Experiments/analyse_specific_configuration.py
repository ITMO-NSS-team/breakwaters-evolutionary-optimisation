import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from CommonUtils.StaticStorage import StaticStorage

seed = 42
np.random.seed(seed)
random.seed(seed)

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

computational_manager = SwanWinRemoteComputationalManager(["125"])
wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 32], [50, 39]])), 0, 'II'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 39]])), 0, 'II'),
    Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [56, 32], [56, 32], [67, 35]])), 0.9, 'IIIa'),
    Breaker('mod3short', list(map(xy_to_points, [[-1, -1], [63, 38], [63, 38], [67, 39]])), 0.9, 'IIIb'),
    Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [56, 42], [56, 42]])), 0.9, '-'),
]

mod_points_to_optimise = {  # order is important
    'mod1': [0],
    'mod2_top': [0],
    'mod2_bottom': [0],
    'mod3long': [0],
    'mod3short': [0],
    'mod_add': [0],
}

selected_modifications_for_tuning = base_modifications_for_tuning
selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

mod_id = "f421fdc533cf41fc9cce7554410e7055-2"



res=wave_model._load_simulation_result_reference_by_id(mod_id)


#hs0 = opt_result.simulation_result.get_output_for_target_points(exp_domain.target_points[0])
