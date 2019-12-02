from functools import partial

from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.DE.DE import DE
from Optimisation import OptimisationTask
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract
from Simulation import WaveModel
from Visualisation.Visualiser import Visualiser


class DEStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask, visualiser: Visualiser):
        problem = partial(calculate_objectives, model, task)

        solution1 = DE(problem, [(0, -45), (5, 45)], popsize=50, dimensions=StaticStorage.genotype_length, maxiters=50,
                       min_or_max=task.goal).solve()

        return solution1
