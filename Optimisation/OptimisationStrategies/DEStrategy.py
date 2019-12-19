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
from EvoAlgs.DE.DefaultDE import DefaultDE
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.SPEA2.Operators import default_operators

from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults


class DEOptimisationStrategy(OptimisationStrategyAbstract):

    def __init__(self, greedy_heuristic=None):
        self.greedy_heuristic = greedy_heuristic

    def optimise(self, model: WaveModel, task: OptimisationTask, visualiser: Visualiser,external_params):
        StaticStorage.multi_objective_optimization = False

        operators = default_operators()

        StaticStorage.max_gens = 5

        if external_params is None:
            external_params = DefaultDE.Params(max_gens=StaticStorage.max_gens, pop_size=5,
                                                  crossover_rate=0.5, mutation_rate=0.5,
                                                  mutation_value_rate=[], min_or_max=task.goal)

        _, archive_history = DefaultDE(
            params=external_params,
            calculate_objectives=partial(calculate_objectives, model, task),
            evolutionary_operators=operators,
            visualiser=visualiser, greedy_heuristic=self.greedy_heuristic).solution(verbose=False)

        best = None

        return OptimisationResults(None, best, archive_history)