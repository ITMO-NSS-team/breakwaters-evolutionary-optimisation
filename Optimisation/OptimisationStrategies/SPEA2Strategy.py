from functools import partial

from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.SPEA2.Operators import default_operators
from Optimisation import OptimisationTask
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults
from Simulation import WaveModel
from Visualisation.Visualiser import Visualiser


class SPEA2OptimisationStrategy(OptimisationStrategyAbstract):

    def __init__(self, greedy_heuristic=None):
        self.greedy_heuristic = greedy_heuristic

    def optimise(self, model: WaveModel, task: OptimisationTask, visualiser: Visualiser, external_params):
        StaticStorage.multi_objective_optimization = True

        operators = default_operators()

        if external_params is None:
            external_params = DefaultSPEA2.Params(max_gens=StaticStorage.max_gens, pop_size=5, archive_size=5,
                                                  crossover_rate=0.5, mutation_rate=0.5,
                                                  mutation_value_rate=[], min_or_max=task.goal)

        _, archive_history = DefaultSPEA2(
            params=external_params,
            calculate_objectives=partial(calculate_objectives, model, task),
            evolutionary_operators=operators,
            visualiser=visualiser, greedy_heuristic=self.greedy_heuristic).solution(verbose=False)

        best = None

        return OptimisationResults(None, best, archive_history)
