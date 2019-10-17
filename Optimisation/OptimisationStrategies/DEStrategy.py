from functools import partial

from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives, print_individuals
from EvoAlgs.DE.DE import DE
from Optimisation import OptimisationTask
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract
from Simulation import WaveModel


class DEStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask):

        #problem = Rastrigin1(dim=2)
        #problem = partial(fitness_function_of_single_objective_optimization, model, task)
        problem = partial(calculate_objectives, model, task)

        print_best_individuals = partial(print_individuals, model, task)
        # problem.plot3d()
        #solution1=DE(problem, [(0, 0),(StaticStorage.exp_domain.base_grid.grid_x, StaticStorage.exp_domain.base_grid.grid_y)],popsize=50,dimensions=2).solve()
        solution1 = DE(problem,print_best_individuals,
                      # [(0, 0), (StaticStorage.exp_domain.base_grid.grid_x, StaticStorage.exp_domain.base_grid.grid_y)],
                       [(0, -45), (20, 45)],
                           popsize=10, dimensions=StaticStorage.genotype_length,maxiters=10).solve()

        return solution1
