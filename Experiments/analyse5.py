import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel, WaveModel
from Simulation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo import EvoOperators
import datetime
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils

from Simulation.ModelVisualization import ModelsVisualization

seed = 42
np.random.seed(seed)
random.seed(seed)

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

computational_manager = SwanWinRemoteComputationalManager(["125"])
wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39]])), 0, '--'),
    Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa')]

mod_points_to_optimise = {  # order is important
    'mod1': [1, 0],
    'mod2_bottom': [0],
    'mod3long': [0]
}

selected_modifications_for_tuning = base_modifications_for_tuning
selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

objectives = [StructuralObjective(importance=1),
              CostObjective(importance=3),
              NavigationObjective(importance=1),
              WaveHeightObjective(importance=2)]

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

mod_id = '904dff5a-6946-434d-8d1d-aaa4e553e6cc'  # custom 1

newg = [33, 25, 36, 26, 57, 41, 56, 29]

brks = BreakersEvoUtils.build_breakers_from_coords(newg, task)

cost = sum([breaker.get_length() for breaker in brks])
costb = sum([breaker.get_length() for breaker in exp_domain.base_breakers])
costa = exp_domain.base_breakers[1].get_length()+exp_domain.base_breakers[2].get_length()+exp_domain.base_breakers[4].get_length()

print((cost)*30-(costb-costa)*30)

wind_walues = [
    "15.0 200", "25.0 200"
]
year_periodicity_labels = [1, 50]

# values * 1.3 (5% to 13%) and calibrated * 1.3
bcond_values = [
    "1.9 6.2 200 30", "7.4 8.4 200 30"
]
ord = 0
for i in [0, 1]:
    for wi in [0, 1]:
        StaticStorage.is_custom_conditions = True
        if wi == 0:
            StaticStorage.wind = "0 0"
        else:
            StaticStorage.wind = wind_walues[i]
        StaticStorage.bdy = bcond_values[i]

        label_to_reference = f'{mod_id}_w{wi}p{year_periodicity_labels[i]}'
        simulation_result = wave_model.run_simulation_for_constructions(wave_model.domain.base_breakers, brks,
                                                                        label_to_reference)

        visualiser = ModelsVisualization(f'{mod_id}_p{year_periodicity_labels[i]}_w{wi}', "experiments")
        visualiser.experimental_visualise(simulation_result.hs, brks, wave_model.domain.base_breakers,
                                          StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points, 5,
                                          [2, 6][i], ['а)', 'б)', 'а)', 'б)'][ord], wi == 1)

        hs0 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[0])
        hs1 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[1])
        hs2 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[2])

        print(f'{hs0},{hs1},{hs2}')
        ord += 1
