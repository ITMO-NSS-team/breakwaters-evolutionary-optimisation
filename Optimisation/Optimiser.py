from Optimisation.OptimisationStrategies.SPEA2Strategy import SPEA2OptimisationStrategy
from Optimisation.OptimisationStrategies.DEStrategy import DEOptimisationStrategy
from Optimisation.OptimisationTask import OptimisationTask
from EvoAlgs.BreakersEvo.GreedyHeurictics.GreedyHeuristic import SequentialGreedyHeurictic


class Optimiser(object):
    def __init__(self, optimisation_strategy):
        self._optimisation_strategy = optimisation_strategy

    def optimise(self, model, task: OptimisationTask, visualiser, external_params = None):
        return self._optimisation_strategy.optimise(model, task, visualiser, external_params)


class DEOptimiser(Optimiser):
    def __init__(self):
        strategy = DEOptimisationStrategy()
        super(DEOptimiser, self).__init__(strategy)


class ParetoEvolutionaryOptimiser(Optimiser):
    def __init__(self):
        spea2_strategy = SPEA2OptimisationStrategy()
        super(ParetoEvolutionaryOptimiser, self).__init__(spea2_strategy)


class GreedyParetoEvolutionaryOptimiser(Optimiser):
    def __init__(self):
        spea2_strategy = SPEA2OptimisationStrategy(greedy_heuristic=SequentialGreedyHeurictic())
        super(GreedyParetoEvolutionaryOptimiser, self).__init__(spea2_strategy)
