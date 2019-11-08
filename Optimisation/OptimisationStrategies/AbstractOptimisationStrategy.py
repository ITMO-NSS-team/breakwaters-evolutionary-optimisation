from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Simulation import WaveModel
from abc import ABCMeta 

# ,EvoOperators, BreakersParams

class OptimisationResults(object):
    def __init__(self, simulation_result, modifications, history):
        self.simulation_result = simulation_result
        self.modifications = modifications
        self.history = history


class OptimisationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def optimise(self, model: WaveModel, task: OptimisationTask) -> OptimisationResults:
        return
