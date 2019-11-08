from functools import partial

from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.SPEA2.Operators import default_operators
from Optimisation import OptimisationTask
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults
from Simulation import WaveModel


class SPEA2OptimisationStrategy(OptimisationStrategyAbstract):

    def optimise(self, model: WaveModel, task: OptimisationTask):
        operators = default_operators()

        _, archive_history = DefaultSPEA2(
            params=DefaultSPEA2.Params(max_gens=100, pop_size=30, archive_size=10,
                                       crossover_rate=0.4, mutation_rate=0.6,  # 0.9 0.9
                                       mutation_value_rate=[]),
            calculate_objectives=partial(calculate_objectives, model, task),
            evolutionary_operators=operators).solution(verbose=False)

        best = archive_history[-1][1]

        return OptimisationResults(None, best, archive_history)
