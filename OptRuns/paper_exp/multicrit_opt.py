import datetime
import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from CommonUtils.StaticStorage import StaticStorage
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from Configuration.Domains import SochiHarbor
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import RelativeCostObjective, RelativeNavigationObjective, RelativeWaveHeightObjective, \
    StructuralObjective, ConstraintComparisonType, RelativeQuailityObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Visualisation.Visualiser import Visualiser, VisualisationSettings, VisualisationData
from EvoAlgs.BreakersEvo.GenotypeEncoders import AngularGenotypeEncoder, CartesianGenotypeEncoder

if __name__ == '__main__':
    seed = 42

    np.random.seed(seed)
    random.seed(seed)

    exp_domain = SochiHarbor()
    StaticStorage.exp_domain = exp_domain

    StaticStorage.is_custom_conditions = True
    StaticStorage.wind = "23.1 135"
    StaticStorage.bdy = "5.3 9.1 200 30"

    EvoAnalytics.clear()
    EvoAnalytics.run_id = 'run_{date:%Y_%m_%d_%H_%M_%S}'.format(date=datetime.datetime.now())

    parallel_computational_manager = SwanWinRemoteComputationalManager(resources_names=["125", "124", "123", "121"])
    wave_model = SwanWaveModel(exp_domain, parallel_computational_manager)
    wave_model.model_results_file_name = 'D:\SWAN_sochi\model_results_paper_martech.db'

    optimiser = ParetoEvolutionaryOptimiser()

    selected_modifications_for_tuning = [
        Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
        Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II')
    ]

    mod_points_to_optimise = {  # order is important
        'mod1': [0],
        'mod2_top': [0]
    }

    optimisation_objectives = [
        RelativeCostObjective(),
        RelativeNavigationObjective(),
        RelativeWaveHeightObjective()]

    analytics_objectives = [
        RelativeQuailityObjective()]

    task = OptimisationTask(optimisation_objectives, selected_modifications_for_tuning, mod_points_to_optimise,
                            goal="minimise")
    task.constraints = [(StructuralObjective(), ConstraintComparisonType.equal, 0)]

    StaticStorage.task = task

    StaticStorage.genotype_encoder = AngularGenotypeEncoder()

    vis_settings = VisualisationSettings(store_all_individuals=False, store_best_individuals=True,
                                         num_of_best_individuals_from_population_for_print=5,
                                         create_gif_image=True,
                                         create_boxplots=True,
                                         print_pareto_front=True)
    vis_data = VisualisationData(optimisation_objectives, base_breakers=exp_domain.base_breakers, task=task)

    visualiser = Visualiser(vis_settings, vis_data)

    opt_result = optimiser.optimise(wave_model, task, visualiser=visualiser)
