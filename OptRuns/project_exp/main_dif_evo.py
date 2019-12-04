import random

import numpy as np

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from Optimisation.Objective import CostObjective, NavigationObjective, StructuralObjective,WaveHeightObjective
from Optimisation.OptimisationTask import OptimisationTask
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser,DEOptimiser
from Simulation.WaveModel import SwanWaveModel
from Computation.СomputationalEnvironment import SwanWinRemoteComputationalManager
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from Visualisation.ModelVisualization import ModelsVisualization
from Visualisation.Visualiser import Visualiser

import datetime

seed = 42
np.random.seed(seed)
random.seed(seed)


#EvoAnalytics.num_of_best_inds_for_print=5
#EvoAnalytics.num_of_generations=5
#EvoAnalytics.gif_images_maker("run_2019_10_03_17_24_59")

'''
EvoAnalytics.run_id="run_DE"
EvoAnalytics.num_of_generations=26
EvoAnalytics.gif_images_maker("run_DE")
EvoAnalytics.united_gif_image_maker("run_DE")
'''
'''
EvoAnalytics.run_id="run_kolya"
EvoAnalytics.num_of_generations=15
EvoAnalytics.create_chart(f="run_kolya",data_for_analyze='obj', analyze_only_last_generation=False,
                                  chart_for_gif=True)
EvoAnalytics.create_chart(f="run_kolya",data_for_analyze='gen_len', analyze_only_last_generation=False,
                                  chart_for_gif=True)
EvoAnalytics.gif_images_maker("run_kolya")
EvoAnalytics.united_gif_image_maker("run_kolya")
'''

exp_domain = SochiHarbor()
StaticStorage.exp_domain = exp_domain

computational_manager = SwanWinRemoteComputationalManager(["125"])
wave_model = SwanWaveModel(exp_domain, None)
#wave_model = SwanWaveModel(exp_domain, computational_manager)

optimiser = DEOptimiser()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [50, 32], [50, 39]])), 0, 'II')
]

mod_points_to_optimise = {  # order is important
    'mod1': [0],
    'mod2_top': [0],
}

selected_modifications_for_tuning = base_modifications_for_tuning
selected_mod_points_to_optimise = [mod_points_to_optimise[mod.breaker_id] for mod in base_modifications_for_tuning]


objectives = [StructuralObjective(),
              CostObjective(),
              NavigationObjective()]
              #WaveHeightObjective(importance=1)]

EvoAnalytics.clear()
EvoAnalytics.run_id = 'run_{date:%Y_%m_%d_%H_%M_%S}'.format(date=datetime.datetime.now())



#EvoAnalytics.create_chart(None,"history_run_2019_08_26_10_12_05.csv",analyze_only_last_generation=False)

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise,goal="minimization" )

StaticStorage.task = task
StaticStorage.genotype_length = len(selected_mod_points_to_optimise) * 2

#print("exp domain",StaticStorage.exp_domain.base_grid.grid_x,"  ",StaticStorage.exp_domain.base_grid.grid_y )
#print("genotype length",StaticStorage.genotype_length)

visualiser=Visualiser(store_all_individuals=False, store_best_individuals=True,num_of_best_individuals_from_population_for_print=5,create_gif_image=True,create_boxplots=True,model=wave_model,task=task)

opt_result = optimiser.optimise(wave_model, task,visualiser)
print("opt_result",opt_result)




hs0 = opt_result.simulation_result.get_5percent_output_for_target_points(exp_domain.target_points[0])

