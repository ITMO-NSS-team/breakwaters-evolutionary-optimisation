from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Visualisation.Visualiser import Visualiser
from abc import ABCMeta, abstractmethod
from Simulation.WaveModel import SwanWaveModel
import csv
import uuid
from functools import partial

from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.SPEA2.Operators import default_operators


# ,EvoOperators, BreakersParams
class OptimisationResults(object):
    def __init__(self, simulation_result, modifications, history):
        self.simulation_result = simulation_result
        self.modifications = modifications
        self.history = history

class OptimisationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def optimise(self, model: WaveModel, task: OptimisationTask, visualiser: Visualiser ) -> OptimisationResults:
        return







