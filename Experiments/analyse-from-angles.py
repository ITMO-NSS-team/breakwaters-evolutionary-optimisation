import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel, WaveModel
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo import EvoOperators
import datetime
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Visualisation.ModelVisualization import ModelsVisualization

seed = 42
np.random.seed(seed)
random.seed(seed)

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39]])), 0, '--'),
    Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa'),
    Breaker('mod3short', list(map(xy_to_points, [[-1, -1], [63, 38], [67, 39]])), 0.9, 'IIIb'),
    Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [56, 42]])), 0.9, '-'),
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

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

# mod_id = "2bae29f1bf1d4b21a7c0fc45c1f48d43"
# mod_id = '9b3a1e81cd694d8a892ec1aa69391a9b'
mod_id = '15cfec8f704f4d3b96fe64a89d270a2a'
# mod_id = 'f5ceed9e0b86467bbdf88b948582cd31'

res = wave_model._load_simulation_result_reference_by_id(mod_id)

geno_from_res = [int(_) for _ in res.split(',')]

newg = []
ord_ind = 0
for m in base_modifications_for_tuning:
    for p in m.points:
        if p.x == -1:
            newg.append(geno_from_res[ord_ind * 2])
            newg.append(geno_from_res[ord_ind * 2 + 1])
        ord_ind += 1

if mod_id == '15cfec8f704f4d3b96fe64a89d270a2a':
    newg[8] = 63
    newg[9] = 38

    newg[4] = 50
    newg[5] = 39

brks = BreakersEvoUtils.build_breakers_from_coords(newg, task)

cost = sum([breaker.get_length() for breaker in brks])
print(cost)

wind_walues = [
    "15.0 157.5",
    "15.0 180",
    "15.0 202.5",
    "17.0 225.0",
    "15.0 247.0",
    "15.0 270.0",

    "22.0 157.5",
    "24.0 180",
    "25.0 202.5",
    "25.0 225.0",
    "23.0 247.0",
    "22.0 270.0",
]

year_periodicity_labels = ['1SSE', '1S', '1SSW', '1SW', '1WSW', '1W', '50SSE', '50S', '50SSW', '50SW', '50WSW', '50W']

# values * 1.3 (5% to 13%) and calibrated * 1.3
bcond_values = [
    "2.6 6.0 157.5 30",
    "2.7 6.2 180.0 30",
    "2.8 6.2 202.5 30",
    "3.3 6.7 225.0 30",
    "2.9 6.5 247.5 30",
    "2.5 6.0 270.0 30",

    "4.2 7.6 157.5 30",
    "5.6 9.1 180.0 30",
    "5.7 8.4 202.5 30",
    "6.2 9.2 225.0 30",
    "5.9 8.7 247.5 30",
    "5.4 8.7 270.0 30",

]
ord = 1
for i in range(0, len(bcond_values)):
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
                                          [2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6][i],
                                          f'{ord})',
                                          wi == 1, [1, 1, 1, 1, 1, 1, 50, 50, 50, 50, 50, 50][i],
                                          ['ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З'][i],
                                          [157.5, 180, 202.5, 225.0, 247.0, 270.0,
                                           157.5, 180, 202.5, 225.0, 247.0, 270.0][i])

        hs0 = simulation_result.get_output_for_target_points(exp_domain.target_points[0])
        hs1 = simulation_result.get_output_for_target_points(exp_domain.target_points[1])
        hs2 = simulation_result.get_output_for_target_points(exp_domain.target_points[2])

        print(f'{hs0},{hs1},{hs2}')
        ord += 1
