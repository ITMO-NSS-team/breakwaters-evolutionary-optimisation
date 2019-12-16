import csv
import os
import random
import datetime
import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from CommonUtils.StaticStorage import StaticStorage
from Configuration.Domains import SochiHarbor, BlackSea
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Visualisation.ModelVisualization import ModelsVisualization
from PIL import Image

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

max2 = 0.5

wave_model.output_time_step = 1


# default
# final

def rotate_90_degree_clckwise(matrix):
    new_matrix = []
    for i in range(len(matrix[0])):
        li = list(map(lambda x: x[i], matrix))
        li.reverse()
        new_matrix.append(li)

    return new_matrix


def angle_to_xy(direction, hs):
    from copy import copy
    length = copy(hs)
    length[length == -9] = 0
    length = length / 5
    rad_grad = 180 / np.pi
    x = length * np.sin(direction / rad_grad)
    y = length * np.cos(direction / rad_grad)
    return x, y

mod_id = "default"

#mod_id = "final"
real_name = mod_id

images = []

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

for _, mod_id in enumerate([real_name]):

    with open(f'F:\\gifs\\hist_{real_name}.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['date', 'hs'])

    if not os.path.isdir(f'img/experiments/{real_name}'):
        os.mkdir(f'img/experiments/{real_name}')

    hs_base = np.genfromtxt(f'D:\\SWAN_sochi\\r\\hs{real_name}_forgif_storm.d')
    dir_base = np.genfromtxt(f'D:\\SWAN_sochi\\r\\dir{real_name}_forgif_storm.d')

    base_date = datetime.datetime(2016, 1, 3, 8, 0, 0)
    ts_ind = 1
    rng = range(8, 8 + 63)
    for ts in rng:  # range(8760+80, 8760+81):#142):
        print(ts)

        wave_model.output_time_step = ts

        label_to_reference = f'HSig'

        ts = wave_model.output_time_step
        start = (ts_ind - 1) * exp_domain.model_grid.grid_y
        end = ts_ind * exp_domain.model_grid.grid_y
        hs = hs_base[start:end]
        dir = dir_base[start:end]

        hs[hs != -9] = hs[hs != -9] / 1.81 * 1.22
        # hs = np.flipud(hs)
        # dir = np.flipud(dir)
        ts_val=hs[exp_domain.target_points[0].y,exp_domain.target_points[0].x]
        ts_date=base_date
        u, v = angle_to_xy(dir-120, hs)
        # hs = np.asarray(rotate_90_degree_clckwise(hs))
        visualiser = ModelsVisualization(ts, mod_id)
        path = visualiser.experimental_small(hs, u, v, all_breakers=brks,
                                      base_breakers=wave_model.domain.base_breakers,
                                      target_points=exp_domain.target_points, vmax=max2)

        images.append(Image.open(path))



        ts_ind = ts_ind + 1
        base_date = base_date + datetime.timedelta(hours=1)

        with open(f'F:\\gifs\\hist_{real_name}.csv', 'a', newline='') as f:
            writer = csv.writer(f, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [ts_date, ts_val])

    images[0].save(f'F://gifs//{real_name}.gif', save_all=True,
                   append_images=images[1:], duration=250,
                   loop=0)



