from Optimisation.Objective import Objective
from typing import List
from Breakers import Breaker


class OptimisationTask(object):
    def __init__(self,
                 objectives: List[Objective],
                 possible_modifications,
                 goal,analytics_objectives):
        self.objectives = objectives
        self.analytics_objectives=analytics_objectives

        self.possible_modifications = possible_modifications

        mod_points_to_optimise = dict()

        for mod in possible_modifications:
            mod_points_to_optimise[mod.breaker_id] = list(
                reversed([ind for ind, pt in enumerate(mod.points) if pt.x == -1 or pt.y == -1]))

        self.mod_points_to_optimise = mod_points_to_optimise
        self.constraints = []
        self.goal = goal
