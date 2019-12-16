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

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

max2 = 0.8

wave_model.output_time_step = 1
# default
# final
real_name = 'BlackSea'

for _, mod_id in enumerate([real_name]):

    if not os.path.isdir(f'img/experiments/{real_name}'):
        os.mkdir(f'img/experiments/{real_name}')

    hs_base = np.genfromtxt(f'D:\\Projects\\Sochi-prichal\\2015\\HSign_20152016_obst_diff.dat')#, skip_header=exp_domain * 100,
                           # max_rows=(142 - 80) * exp_domain.model_grid.grid_x)
    base_date = datetime.datetime(2015, 9, 25, 0, 0, 0)
    ts_ind = 1
    for ts in range(1,4537):
        #print(ts)

        wave_model.output_time_step = ts

        label_to_reference = f'HSig'

        ts = wave_model.output_time_step
        start = (ts_ind - 1) * exp_domain.model_grid.grid_y
        end = ts_ind * exp_domain.model_grid.grid_y
        hs = hs_base[start:end]
        hs[hs != -9] = hs[hs != -9] / 1.81 * 1.22
        #hs = np.flipud(hs)
        # hs = np.asarray(rotate_90_degree_clckwise(hs))
        #visualiser = ModelsVisualization(ts, mod_id)
        #visualiser.experimental_visualise_large(hs, max2, base_date)
        ts_ind = ts_ind + 1
        base_date = base_date + datetime.timedelta(hours=1)

        hs0 = hs[39,64]
        print(f'{ts},{base_date},{round(hs0,2)}')


