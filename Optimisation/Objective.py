from abc import ABCMeta, abstractmethod
import numpy as np
from Configuration.Domains import Domain, Fairway
from Breakers.Breaker import Breaker
from typing import List
from Simulation.Results import SimulationResult, WaveSimulationResult


class Objective(object):
    @abstractmethod
    def get_obj_value(self, domain: Domain, breakers: List[Breaker]):
        return


class CostObjective(Objective):
    relative_cost = 0.1

    def get_obj_value(self, domain, breakers):
        cost = sum([breaker.get_length() for breaker in breakers])
        return cost


class NavigationObjective(Objective):

    def _dist_from_fairway_to_breaker(self, fairway: Fairway, breaker: Breaker):
        p1 = np.asarray([fairway.x1, fairway.y1])
        p2 = np.asarray([fairway.x2, fairway.y2])
        dist = min([np.linalg.norm(np.cross(p2 - p1, p1 - np.asarray([p3.x, p3.y]))) / np.linalg.norm(p2 - p1) for p3 in
                    breaker.points])

        return dist

    def get_obj_value(self, domain, breakers):
        min_dist_to_fairway = min(min(
            [[(self._dist_from_fairway_to_breaker(fairway, breaker) / fairway.importance) for breaker in breakers] for
             fairway in
             domain.fairways]))
        navigation_difficultness = 1 / min_dist_to_fairway
        return navigation_difficultness


class WaveHeightObjective(Objective):

    def get_obj_value(self, domain, breakers, simulation_result: WaveSimulationResult):
        hs_vals = simulation_result.get_output_for_target_points(domain.target_points)

        hs_weigtened = [hs * pt.weight for hs, pt in zip(hs_vals, domain.target_points)]

        return np.mean(hs_weigtened) + 0.05  # to avoid zero


class WaveHeightMultivariateObjective(Objective):

    def get_obj_value(self, domain, breakers, simulation_result: WaveSimulationResult):
        hs_vals = simulation_result.get_output_for_target_points(domain.target_points)

        hs_weigtened = [hs * pt.weight for hs, pt in zip(hs_vals, domain.target_points)]

        return [(hs + 0.05) for hs in hs_weigtened]  # to avoid zero
