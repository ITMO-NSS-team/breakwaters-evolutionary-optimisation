import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor, ExpHarbor
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective, RelativeQuailityObjective
from Optimisation.OptimisationTask import OptimisationTask
from Visualisation.Visualiser import Visualiser
import datetime

if __name__ == '__main__':
    seed = 42

    np.random.seed(seed)
    random.seed(seed)

    exp_domain = ExpHarbor()
    StaticStorage.exp_domain = exp_domain

    StaticStorage.is_custom_conditions = True
    StaticStorage.wind = "23.1 135"
    StaticStorage.bdy = "5.3 9.1 200 30"

    EvoAnalytics.clear()
    EvoAnalytics.run_id = 'run_{date:%Y_%m_%d_%H_%M_%S}'.format(date=datetime.datetime.now())

    parallel_computational_manager = SwanWinRemoteComputationalManager(resources_names=["125", "124", "123"],
                                                                       is_lazy_parallel=True)
    wave_model = SwanWaveModel(exp_domain, None)
    wave_model.model_results_file_name = 'D:\SWAN_sochi\model_results_addexp6.db'

    optimiser = ParetoEvolutionaryOptimiser()

    base_modifications_for_tuning = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II')
    ]

    mod_points_to_optimise = {  # order is important
        'mod1': [0],
        'mod2_top': [0]
    }

    selected_modifications_for_tuning = base_modifications_for_tuning
    selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in
                                       base_modifications_for_tuning
                                       if mod.breaker_id in mod_points_to_optimise]

    objectives = [RelativeQuailityObjective()]

    task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, goal="minimization")
    task.strict_objectives = []

    StaticStorage.task = task
    StaticStorage.genotype_length = sum([len(_) * 2 for _ in selected_mod_points_to_optimise])

    visualiser = Visualiser(store_all_individuals=False, store_best_individuals=True,
                            num_of_best_individuals_from_population_for_print=5, create_gif_image=True,
                            create_boxplots=True, model=wave_model, task=task)

    opt_result = optimiser.optimise(wave_model, task,visualiser)

