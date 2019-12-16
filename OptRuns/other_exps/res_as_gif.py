import csv
import os
import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from CommonUtils.StaticStorage import StaticStorage
from Configuration.Domains import SochiHarbor
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Visualisation.ModelVisualization import ModelsVisualization

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain



wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

max2 = 0.7

wave_model.output_time_step = 1
#default
#final
for _, mod_id in enumerate(['final']):

    real_name = mod_id
    lensb = ([breaker.get_length() for breaker in exp_domain.base_breakers])

    if mod_id == 'default':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39]])), 0, '--'),
            Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa')]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
            'mod3long': [1, 0]
        }

        newg = [30, 30, 57, 41, 56, 30, 58, 29]

        lensb_real = [lensb[0], 0, lensb[3]]
        brks = exp_domain.base_breakers
    elif mod_id == 'final':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39]])), 0, '--'),
            Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa')
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_top': [0],
            'mod2_bottom': [0],
            'mod3long': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [32, 27, 50, 30, 56, 40, 56, 33]

        selected_modifications_for_tuning = base_modifications_for_tuning
        selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in
                                           base_modifications_for_tuning]

        objectives = [StructuralObjective(),
                      CostObjective(),
                      NavigationObjective(),
                      WaveHeightObjective()]

        task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, None)

        brks = BreakersEvoUtils.build_breakers_from_manual_coords(newg, task)

    lens = [breaker.get_length() for breaker in brks]

    sum_len = [int(round((x1 - x2))) * 25 for (x1, x2) in zip(lens, lensb_real)]

    all_labels = [
        'торец оградит. мола',
        'торец №1 волнолома',
        'торец №2 волнолома',
        'торец сев. оградит. мола',
        'торец причала ФСО',
        'торец южн. оградит. мола'
    ]

    len_info = ""
    lind = 0
    for i, _len in enumerate(sum_len):
        if _len > 1:
            new1 = ', '
            if lind % 2 == 1:
                new1 = ',\n '
            lind += 1
            if mod_id in ['MKG9_Т8_75', 'MKG10_Т6_75'] and i == 1:
                len_info += f'{all_labels[i]}: 75 м{new1}'
            else:
                len_info += f'{all_labels[i]}: {_len} м{new1}'

    len_info = len_info[0:(len(len_info) - 3)]
    len_info += '.\n'

    wind_walues = [
        "15.0 135.0",
        "15.0 157.5",
        "15.0 180",
        "15.0 202.5",
        "17.0 225.0",
        "15.0 247.0",
        "15.0 270.0",
        "20.0 135.0",
        "22.0 157.5",
        "24.0 180",
        "25.0 202.5",
        "25.0 225.0",
        "23.0 247.0",
        "22.0 270.0",
        "23.1 135",
    ]

    year_periodicity_labels = ['1SE', '1SSE', '1S', '1SSW', '1SW', '1WSW', '1W', '50SE', '50SSE', '50S', '50SSW',
                               '50SW',
                               '50WSW',
                               '50W']

    # values * 1.3 (5% to 13%) and calibrated * 1.3
    bcond_values = [
        "2.3 6.0 135.0 30",
        "2.6 6.0 157.5 30",
        "2.7 6.2 180.0 30",
        "2.8 6.2 202.5 30",
        "3.3 6.7 225.0 30",
        "2.9 6.5 247.5 30",
        "2.5 6.0 270.0 30",
        "3.8 7.6 135.0 30",
        "4.2 7.6 157.5 30",
        "5.6 9.1 180.0 30",
        "5.7 8.4 202.5 30",
        "6.2 9.2 225.0 30",
        "5.9 8.7 247.5 30",
        "5.4 8.7 270.0 30",
    ]

    bcond_values0 = [
        "2.8 6.2 202.5",
        "5.7 8.4 202.5 30"
    ]

    wind_walues0 = [
        "15.0 202.5", "25.0 202.5"
    ]

    if not os.path.isdir(f'img/experiments/{real_name}'):
        os.mkdir(f'img/experiments/{real_name}')

    #rng = range(80,142)
    #if mod_id =="final":
    rng=range(80-24, 142-24)
    for ts in rng:
        #print(ts)
        wave_model.output_time_step = ts

        bord = 0
        wi = 1
        sign = 2
        i = 1
        StaticStorage.is_custom_conditions = True
        if wi == 0:
            StaticStorage.wind = "0 0"
        else:
            StaticStorage.wind = wind_walues0[i]
        StaticStorage.bdy = bcond_values0[i]

        label_to_reference = f'{mod_id}_forgif_storm'
        simulation_result = wave_model.run_simulation_for_constructions(brks,
                                                                        label_to_reference)

        if True:
            visualiser = ModelsVisualization(ts, real_name)
            visualiser.experimental_visualise(simulation_result.get_mean_output_for_field(), brks,
                                              wave_model.domain.base_breakers,
                                              StaticStorage.exp_domain.fairways,
                                              StaticStorage.exp_domain.target_points,
                                              "mean",
                                              [2, max2][i],
                                              'а)',
                                              wi == 1, [1, 50][i],
                                              None,
                                              200.0,
                                              len_info)


        hs0 = simulation_result.get_mean_output_for_target_points(exp_domain.target_points[0])
        hs1 = simulation_result.get_mean_output_for_target_points(exp_domain.target_points[1])
        hs2 = simulation_result.get_mean_output_for_target_points(exp_domain.target_points[2])

        print(f'{round(hs0,2)},{round(hs1,2)},{round(hs2,2)}')


        bord += 1
