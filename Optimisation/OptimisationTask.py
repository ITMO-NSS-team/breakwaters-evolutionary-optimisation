from Optimisation.Objective import Objective
from typing import List
from Breakers import Breaker


class OptimisationTask(object):
    def __init__(self,
                 objectives: List[Objective],
                 possible_modifications,  #: List[Breaker],
                 mod_points_to_optimise: List):
        self.objectives = objectives
        self.possible_modifications = possible_modifications
        self.mod_points_to_optimise = mod_points_to_optimise
