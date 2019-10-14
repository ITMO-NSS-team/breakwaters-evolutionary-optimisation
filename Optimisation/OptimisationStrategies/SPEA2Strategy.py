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

from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives,print_individuals
from EvoAlgs.SPEA2.Operators import default_operators

from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults


class SPEA2OptimisationStrategy(OptimisationStrategyAbstract):

    def optimise(self, model: WaveModel, task: OptimisationTask):
        operators = default_operators()


        _, archive_history = DefaultSPEA2(
            params=DefaultSPEA2.Params(max_gens=8, pop_size=50, archive_size=50,
                                       crossover_rate=0.6, mutation_rate=0.3,#0.9 0.9
                                       mutation_value_rate=[]),
            objectives=partial(calculate_objectives, model, task),print_func = partial(print_individuals, model, task),
            evolutionary_operators=operators).solution(verbose=False)

        best = archive_history[-1][1]

        return OptimisationResults(None, best, archive_history)
