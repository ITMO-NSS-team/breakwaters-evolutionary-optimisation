import csv
import random

import numpy as np
import os

from Breakers.Breaker import xy_to_points, Breaker
from CommonUtils.StaticStorage import StaticStorage
from Configuration.Domains import SochiHarbor
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Visualisation.ModelVisualization import ModelsVisualization

seed = 42
np.random.seed(seed)
random.seed(seed)

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

for mod_id in ['n11_cover','n11_25c', 'n11_50', 'n11_75', 'n11_125', 'n11_250', 'n11_125_2', 'n11_125realaga_2', 'n11_50_3',
               'n11_75_3',
               'n11_50_3ext', 'n11_closed', 'n11_0']:

    lensb = ([breaker.get_length() for breaker in exp_domain.base_breakers])
    if mod_id == 'n11_0':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50, 39]
    elif mod_id == 'n11_25c':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50, 39 + 1]
    elif mod_id == 'n11_50':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50, 39 + 2]
    elif mod_id == 'n11_75':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50, 39 + 3]

    elif mod_id == 'n11_125':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50, 39 + 5]
    elif mod_id == 'n11_250':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50, 39 + 10]
    elif mod_id == 'n11_cover':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 56,41]
    elif mod_id == 'n11_closed':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-')
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_top': [0],
            'mod2_bottom': [0]
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 56, 32, 50, 39 + 10]
    elif mod_id == 'n11_125_2':  # really 75
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50 - 2, 39 + 2]
    elif mod_id == 'n11_125realaga_2':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 50 - 3, 39 + 4]
    elif mod_id == 'n11_50_3':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [56, 40], [56, 41]])), 0.9, '-')
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod_add': [0]
        }

        lensb_real = [lensb[0], lensb[2]]

        newg = [30, 25, 54, 40]
    elif mod_id == 'n11_75_3':
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [56, 40], [56, 41]])), 0.9, '-')
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod_add': [0]
        }

        lensb_real = [lensb[0], 25]

        newg = [30, 25, 53, 40]
    elif mod_id == 'n11_50_3ext':  # +75
        base_modifications_for_tuning = [
            Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
            Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [50, 39], [50, 32]])), 0, '-'),
            Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [56, 40], [56, 41]])), 0.9, '-')
        ]

        mod_points_to_optimise = {  # order is important
            'mod1': [0],
            'mod2_bottom': [0],
            'mod_add': [0]
        }

        lensb_real = [lensb[0], 25]

        newg = [30, 25, 50, 39 + 3, 54, 40]

    selected_modifications_for_tuning = base_modifications_for_tuning
    selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

    objectives = [StructuralObjective(importance=1),
                  CostObjective(importance=3),
                  NavigationObjective(importance=1),
                  WaveHeightObjective(importance=2)]

    task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

    brks = BreakersEvoUtils.build_breakers_from_coords(newg, task)

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

    if not os.path.isdir(f'img/experiments/{mod_id}'):
        os.mkdir(f'img/experiments/{mod_id}')

    with open(f'img/experiments/{mod_id}/{mod_id}-base-fortab.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['hs1', 'hs2', 'hs3'])

    bord = 0
    for wi in [1]:  # [0, 1]:
        for sign in [1]:  # [0, 1]:
            for i in [1]:  # [0, 1]:
                StaticStorage.is_custom_conditions = True
                if wi == 0:
                    StaticStorage.wind = "0 0"
                else:
                    StaticStorage.wind = wind_walues0[i]
                StaticStorage.bdy = bcond_values0[i]

                label_to_reference = f'{mod_id}_w{wi}p{i}_s'
                simulation_result = wave_model.run_simulation_for_constructions(brks,
                                                                                label_to_reference)
                if sign == 1:
                    visualiser = ModelsVisualization(label_to_reference, mod_id)
                    visualiser.experimental_visualise(simulation_result.get_13percent_output_for_field(), brks,
                                                      wave_model.domain.base_breakers,
                                                      StaticStorage.exp_domain.fairways,
                                                      StaticStorage.exp_domain.target_points,
                                                      13,
                                                      [2, 6][i],
                                                      # ['а)', 'б)', 'а)', 'б)'][bord],
                                                      'а)',
                                                      wi == 1, [1, 50][i],
                                                      'ЮЮЗ',
                                                      200.0,
                                                      len_info)

                if sign == 0:
                    hs0 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[0])
                    hs1 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[1])
                    hs2 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[2])
                else:
                    hs0 = simulation_result.get_13percent_output_for_target_points(exp_domain.target_points[0])
                    hs1 = simulation_result.get_13percent_output_for_target_points(exp_domain.target_points[1])
                    hs2 = simulation_result.get_13percent_output_for_target_points(exp_domain.target_points[2])

                print(f'{hs0},{hs1},{hs2}')

                with open(f'img/experiments/{mod_id}/{mod_id}-base-fortab.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter='\t',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([round(hs0, 2), round(hs1, 2), round(hs2, 2)])

                bord += 1

if False:
    wave_model.model_results_file_name = "D:\\SWAN_sochi\\model_results.db"

    with open(f'img/experiments/{mod_id}/{mod_id}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['is_wind', 'rep', 'dir', 'hs1', 'hs2', 'hs3'])

    with open(f'img/experiments/{mod_id}/{mod_id}-fortab.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['hs1', 'hs2', 'hs3'])

    for sign in [0, 1]:
        ord = 0
        for wi in [0, 1]:
            for i in range(0, len(bcond_values)):
                print(ord)
                StaticStorage.is_custom_conditions = True
                if wi == 0:
                    StaticStorage.wind = "0 0"
                else:
                    StaticStorage.wind = wind_walues[i]
                StaticStorage.bdy = bcond_values[i]

                label_to_reference = f'{mod_id}_w{wi}p{year_periodicity_labels[i]}'
                simulation_result = wave_model.run_simulation_for_constructions(brks,
                                                                                label_to_reference)

                if sign == 1 and i == 9 - 1:  #
                    # ord == 14+15 and sign == 1 #and [1, 1, 1, 1, 1, 1, 1, 50, 50, 50, 50, 50, 50, 50][i]==50:
                    print("SSE")
                    visualiser = ModelsVisualization(f'{mod_id}_p{year_periodicity_labels[i]}_w{wi}', mod_id)
                    visualiser.experimental_visualise(simulation_result.get_13percent_output_for_field(), brks,
                                                      wave_model.domain.base_breakers,
                                                      StaticStorage.exp_domain.fairways,
                                                      StaticStorage.exp_domain.target_points,
                                                      13,
                                                      [2, 2, 2, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6][i],
                                                      # f'{ord})',
                                                      'б)',
                                                      wi == 1, [1, 1, 1, 1, 1, 1, 1, 50, 50, 50, 50, 50, 50, 50][i],
                                                      ['ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЮВ', 'ЮЮВ', 'Ю',
                                                       'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З',
                                                       'ЮЮЗ'][i],
                                                      [135.0, 157.5, 180, 202.5, 225.0, 247.0, 270.0,
                                                       135.0, 157.5, 180, 202.5, 225.0, 247.0, 270.0, ][i],
                                                      len_info)
                if sign == 0:
                    hs0 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[0])
                    hs1 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[1])
                    hs2 = simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[2])
                else:
                    hs0 = simulation_result.get_13percent_output_for_target_points(exp_domain.target_points[0])
                    hs1 = simulation_result.get_13percent_output_for_target_points(exp_domain.target_points[1])
                    hs2 = simulation_result.get_13percent_output_for_target_points(exp_domain.target_points[2])
                print(f'{hs0},{hs1},{hs2}')

                print(f'{hs0},{hs1},{hs2}')

                ord += 1
                with open(f'img/experiments/{mod_id}/{mod_id}.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=' ',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([wi, [1, 1, 1, 1, 1, 1, 1, 50, 50, 50, 50, 50, 50, 50][i],
                                     ['ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З', 'ЮВ', 'ЮЮВ',
                                      'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ', 'З'][i], round(hs0, 2), round(hs1, 2),
                                     round(hs2, 2)])

                with open(f'img/experiments/{mod_id}/{mod_id}-fortab.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter='\t',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([round(hs0, 2), round(hs1, 2), round(hs2, 2)])
