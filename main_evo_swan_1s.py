import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Simulation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo import EvoOperators
import datetime
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils

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

objectives = [StructuralObjective(importance=1),
              CostObjective(importance=3),
              NavigationObjective(importance=1),
                WaveHeightObjective(importance=2)]

EvoAnalytics.clear()
EvoAnalytics.run_id = 'run_{date:%Y_%m_%d_%H_%M_%S}'.format(date=datetime.datetime.now())
#print(EvoAnalytics.run_id)
EvoAnalytics.chart_series_creator(f="history_run_2019_08_26_10_12_05.csv")

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

StaticStorage.task = task
StaticStorage.genotype_length = len(selected_mod_points_to_optimise)*2

opt_result = optimiser.optimise(wave_model, task)

hs0 = opt_result.simulation_result.get_output_for_target_points(exp_domain.target_points[0])
