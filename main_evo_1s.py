import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Objective import CostObjective, NavigationObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
import datetime

seed = 42
np.random.seed(seed)
random.seed(seed)

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

computational_manager = SwanWinRemoteComputationalManager(["125"])
wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II')
]

mod_points_to_optimise = {  # order is important
    'mod1': [0],
    'mod2_top': [0],
}

selected_modifications_for_tuning = base_modifications_for_tuning
selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

objectives = [StructuralObjective(importance=1),
              CostObjective(importance=3),
              NavigationObjective(importance=1)]

EvoAnalytics.clear()
EvoAnalytics.run_id = 'run_{date:%Y_%m_%d_%H_%M_%S}'.format(date=datetime.datetime.now())

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

StaticStorage.task = task
StaticStorage.genotype_length = len(selected_mod_points_to_optimise) * 2

opt_result = optimiser.optimise(wave_model, task)

hs0 = opt_result.simulation_result.get_output_for_target_points(exp_domain.target_points[0])
