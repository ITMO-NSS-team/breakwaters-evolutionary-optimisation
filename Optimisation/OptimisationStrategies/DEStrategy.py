from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Simulation.WaveModel import SwanWaveModel
from EvoAlgs.DE.DE import DE
from EvoAlgs.DE.Problems import Rastrigin1
import csv
import uuid
from functools import partial
import numpy as np
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives,fitness_function_of_single_objective_optimization
from EvoAlgs.SPEA2.Operators import default_operators

from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults

class DEStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask):

        #problem = Rastrigin1(dim=2)
        #problem = partial(fitness_function_of_single_objective_optimization, model, task)
        problem = partial(calculate_objectives, model, task)
        # problem.plot3d()
        #solution1=DE(problem, [(0, 0),(StaticStorage.exp_domain.base_grid.grid_x, StaticStorage.exp_domain.base_grid.grid_y)],popsize=50,dimensions=2).solve()
        solution1 = DE(problem,
                       [(0, 0), (StaticStorage.exp_domain.base_grid.grid_x, StaticStorage.exp_domain.base_grid.grid_y)],
                       popsize=50, dimensions=StaticStorage.genotype_length).solve()

        return solution1
