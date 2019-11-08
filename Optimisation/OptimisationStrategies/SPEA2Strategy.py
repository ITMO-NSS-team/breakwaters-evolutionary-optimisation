from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Simulation.WaveModel import SwanWaveModel
import csv
import uuid
from functools import partial
from Visualisation.Visualiser import Visualiser
from CommonUtils.StaticStorage import StaticStorage

from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives,print_best_individuals_for_gif
from EvoAlgs.SPEA2.Operators import default_operators

from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults


class SPEA2OptimisationStrategy(OptimisationStrategyAbstract):

    def optimise(self, model: WaveModel, task: OptimisationTask,visualiser: Visualiser):
        StaticStorage.multi_objective_optimization=True

        operators = default_operators()


        _, archive_history = DefaultSPEA2(
            params=DefaultSPEA2.Params(max_gens=5, pop_size=10, archive_size=10,
                                       crossover_rate=0.6, mutation_rate=0.3,#0.9 0.9
                                       mutation_value_rate=[],min_or_max=task.goal),
            objectives=partial(calculate_objectives, model, task,visualiser,multi_objective_optimization=True),
            evolutionary_operators=operators).solution(verbose=False)

        best = archive_history[-1][1]

        return OptimisationResults(None, best, archive_history)
