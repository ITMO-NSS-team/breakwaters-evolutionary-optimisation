from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Simulation.WaveModel import SwanWaveModel
import csv
import uuid
from functools import partial

from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.SPEA2.Operators import default_operators
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults


class ManualOptimisationStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask):
        modifications = task.possible_modifications

        # TODO: run all combinations and find best

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, modifications)

        return OptimisationResults(simulation_result, modifications, [])
