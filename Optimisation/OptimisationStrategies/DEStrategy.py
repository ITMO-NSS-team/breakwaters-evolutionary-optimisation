from functools import partial

from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.DE.DE import DE
from Optimisation import OptimisationTask
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract
from Simulation import WaveModel
from Visualisation.Visualiser import Visualiser

class DEStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask,visualiser: Visualiser ):
        StaticStorage.multi_objective_optimization = False
        problem = partial(calculate_objectives, model, task,visualiser,multi_objective_optimization=False)

        solution1 = DE(problem,[(0, -45), (20, 45)], popsize=10, dimensions=StaticStorage.genotype_length,maxiters=5,min_or_max=task.goal).solve()

        return solution1
