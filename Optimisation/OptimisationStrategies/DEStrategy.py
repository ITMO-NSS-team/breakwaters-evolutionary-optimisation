from functools import partial

from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives, print_best_individuals_for_gif
from EvoAlgs.DE.DE import DE
from Optimisation import OptimisationTask
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract
from Simulation import WaveModel
from Visualisation.Visualiser import Visualiser

class DEStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask,visualiser: Visualiser ):
        StaticStorage.multi_objective_optimization = False
        problem = partial(calculate_objectives, model, task,visualiser,multi_objective_optimization=False)

        #print_best_individuals = partial(print_individuals, model, task)

        print_best_individuals = partial(print_best_individuals_for_gif, model, task)

        solution1 = DE(problem,print_best_individuals,
                      # [(0, 0), (StaticStorage.exp_domain.base_grid.grid_x, StaticStorage.exp_domain.base_grid.grid_y)],
                       [(0, -45), (20, 45)],
                           popsize=10, dimensions=StaticStorage.genotype_length,maxiters=5,min_or_max=task.goal).solve()

        return solution1
