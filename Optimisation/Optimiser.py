
from Optimisation.OptimisationStrategies.SPEA2Strategy import SPEA2OptimisationStrategy

from Optimisation.OptimisationStrategies.DEStrategy import DEStrategy


from Optimisation.OptimisationTask import OptimisationTask


class Optimiser(object):
    def __init__(self, optimisation_strategy):
        self._optimisation_strategy = optimisation_strategy

    def optimise(self, model, task: OptimisationTask,visualiser):
        return self._optimisation_strategy.optimise(model, task,visualiser)


class DEOptimiser(Optimiser):
    def __init__(self):
        strategy = DEStrategy()
        super(DEOptimiser, self).__init__(strategy)


class ParetoEvolutionaryOptimiser(Optimiser):
    def __init__(self):
        spea2_strategy = SPEA2OptimisationStrategy()
        super(ParetoEvolutionaryOptimiser, self).__init__(spea2_strategy)
