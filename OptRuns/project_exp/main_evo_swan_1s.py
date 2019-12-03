import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Visualisation.Visualiser import Visualiser
import datetime
import itertools
import matplotlib.pyplot as plt

if __name__ == '__main__':
    seed = 91429  # random.randint(1,10001)

    # 42
    np.random.seed(seed)
    random.seed(seed)

    exp_domain = SochiHarbor()
    StaticStorage.exp_domain = exp_domain

    StaticStorage.is_custom_conditions = True
    StaticStorage.wind = "23.1 135"
    StaticStorage.bdy = "5.3 9.1 200 30"

    EvoAnalytics.clear()
    EvoAnalytics.run_id = 'run_{date:%Y_%m_%d_%H_%M_%S}'.format(date=datetime.datetime.now())

    # wave_model = SwanWaveModel(exp_domain, None)

    parallel_computational_manager = SwanWinRemoteComputationalManager(resources_names=["125", "124", "123", '121'],
                                                                       is_lazy_parallel=True)
    wave_model = SwanWaveModel(exp_domain, parallel_computational_manager)

    optimiser = ParetoEvolutionaryOptimiser()

    base_modifications_for_tuning = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 39]])), 0, 'II'),
        Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 39], [50, 32]])), 0, '-')
    ]

    mod_points_to_optimise = {  # order is important
        'mod1': [1, 0],
        'mod2_top': [1, 0],
        'mod2_bottom': [1, 0],
    }

    selected_modifications_for_tuning = base_modifications_for_tuning
    selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]

    objectives = [StructuralObjective(importance=1),
                  CostObjective(importance=3),
                  NavigationObjective(importance=1),
                  WaveHeightObjective(importance=2)]

    task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, goal="minimization")

    StaticStorage.task = task
    StaticStorage.genotype_length = sum([len(_) * 2 for _ in selected_mod_points_to_optimise])

    visualiser = Visualiser(store_all_individuals=False, store_best_individuals=True,
                            num_of_best_individuals_from_population_for_print=5, create_gif_image=True,
                            create_boxplots=True, model=wave_model, task=task, print_pareto_front=True,
                            data_for_pareto_set_chart=[["hs average decrease", "cost"]])
    opt_result = optimiser.optimise(wave_model, task, visualiser)

    '''
    min_x = min(list(itertools.chain(*StaticStorage.mean_hhs)))
    max_x = max(list(itertools.chain(*StaticStorage.mean_hhs)))
    min_y = min(list(itertools.chain(*StaticStorage.costs)))
    max_y = max(list(itertools.chain(*StaticStorage.costs)))
    for i in range(len(StaticStorage.mean_hhs)):
        fig, ax = plt.subplots()
        #ax.set_title("Популяция " + str(i + 1))
        ax.set_xlabel("Среднее снижение hs по всем точкам", fontsize=15)
        ax.set_ylabel("Цена", fontsize=15)
        ax.scatter(StaticStorage.mean_hhs[i], StaticStorage.costs[i], linewidths=7, color='g')
        plt.tick_params(axis='both', labelsize=15)
        plt.ylim(min_y-1, max_y+1)
        plt.xlim(min_x-1, max_x+1)
        fig.set_figwidth(7)
        fig.set_figheight(7)
        plt.savefig(f'pareto_front/img/{str(EvoAnalytics.run_id)}/{i}.png', bbox_inches='tight')
    '''

    hs0 = opt_result.simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[0])
