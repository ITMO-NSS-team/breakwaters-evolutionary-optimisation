from abc import ABCMeta, abstractmethod

from Optimisation import OptimisationTask
from Simulation import WaveModel
from Visualisation.Visualiser import Visualiser

class OptimisationResults(object):
    def __init__(self, simulation_result, modifications, history):
        self.simulation_result = simulation_result
        self.modifications = modifications
        self.history = history


class OptimisationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def optimise(self, model: WaveModel, task: OptimisationTask, visualiser: Visualiser) -> OptimisationResults:
        return
