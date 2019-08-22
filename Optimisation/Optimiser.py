from Optimisation.OptimisationStrategies.DiffirentialEvoStrategy import DifferentialOptimisationStrategy
from Optimisation.OptimisationStrategies.ManualStrategy import ManualOptimisationStrategy
from Optimisation.OptimisationStrategies.EmptyStrategy import EmptyOptimisationStrategy
from Optimisation.OptimisationStrategies.SPEA2Strategy import SPEA2OptimisationStrategy

from Optimisation.OptimisationTask import OptimisationTask


class Optimiser(object):
    def __init__(self, optimisation_strategy):
        self._optimisation_strategy = optimisation_strategy

    def optimise(self, model, task: OptimisationTask):
        return self._optimisation_strategy.optimise(model, task)


class StubOptimiser(Optimiser):
    def __init__(self):
        emp_strategy = EmptyOptimisationStrategy()
        super(StubOptimiser, self).__init__(emp_strategy)


class ManualOptimiser(Optimiser):
    def __init__(self):
        man_strategy = ManualOptimisationStrategy()
        super(ManualOptimiser, self).__init__(man_strategy)


class DifferentialEvolutionaryOptimiser(Optimiser):
    def __init__(self):
        deoptim_strategy = DifferentialOptimisationStrategy()
        super(DifferentialEvolutionaryOptimiser, self).__init__(deoptim_strategy)


class ParetoEvolutionaryOptimiser(Optimiser):
    def __init__(self):
        spea2_strategy = SPEA2OptimisationStrategy()
        super(ParetoEvolutionaryOptimiser, self).__init__(spea2_strategy)
