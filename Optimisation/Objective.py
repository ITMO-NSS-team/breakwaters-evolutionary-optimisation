from abc import ABCMeta, abstractmethod
import numpy as np
from Configuration.Domains import Domain, Fairway
from Breakers.Breaker import Breaker
from typing import List
from Simulation.Results import SimulationResult, WaveSimulationResult
from shapely.geometry import LineString


class Objective(object):
    @abstractmethod
    def get_obj_value(self, domain: Domain, breakers: List[Breaker]):
        return

    def __init__(self, importance=1):
        self.importance = importance


class StructuralObjective(Objective):

    def _selfintersection(self, breaker1, breaker2):
        for i in range(1, len(breaker1.points)):
            prev1 = breaker1.points[i - 1]
            cur1 = breaker1.points[i]

            if prev1.x == cur1.x and \
                    prev1.y == cur1.y:
                continue

            breaker_line1 = LineString([(prev1.x, prev1.y), (cur1.x, cur1.y)])
            for j in range(1, len(breaker2.points)):
                prev2 = breaker2.points[j - 1]
                cur2 = breaker2.points[j]

                if prev2.x == cur2.x and \
                        prev2.y == cur2.y:
                    continue

                if prev1.x == prev2.x and \
                        prev1.y == prev2.y:
                    continue

                if prev1.x == cur2.x and \
                        prev1.y == cur2.y:
                    continue

                if prev2.x == cur1.x and \
                        prev2.y == cur1.y:
                    continue

                if cur1.x == cur2.x and \
                        cur1.y == cur2.y:
                    continue

                if prev1.x == prev2.x and \
                        prev1.y == prev2.y:
                    continue

                breaker_line2 = LineString([(prev2.x, prev2.y), (cur2.x, cur2.y)])

                if breaker_line1.crosses(breaker_line2):
                    return True
        return False

    def get_obj_value(self, domain, breakers):

        num_self_intersection = sum(
            [sum([int(self._selfintersection(breaker1, breaker2)) for breaker2 in breakers]) for breaker1 in breakers])

        return round(num_self_intersection * 100, -1)


class CostObjective(Objective):

    def get_obj_value(self, domain, breakers):
        cost = sum([breaker.get_length() for breaker in breakers]) * 10
        return round(cost, -1)


class NavigationObjective(Objective):

    def _dist_from_fairway_to_breaker(self, fairway: Fairway, breaker: Breaker):
        def intersections_count(fairway, breaker):
            fairway_line = LineString([(fairway.x1, fairway.y1), (fairway.x2, fairway.y2)])
            int_num = 0
            for i in range(1, len(breaker.points)):
                prev = breaker.points[i - 1]
                cur = breaker.points[i]
                if prev.x == cur.x and \
                        prev.y == cur.y:
                    continue
                breaker_line = LineString([(prev.x, prev.y), (cur.x, cur.y)])
                if fairway_line.crosses(breaker_line):
                    int_num = int_num + 1
            return int_num

        int_count = intersections_count(fairway, breaker)
        if int_count > 0:
            return -int_count
        p1 = np.asarray([fairway.x1, fairway.y1])
        p2 = np.asarray([fairway.x2, fairway.y2])
        dist = min([np.linalg.norm(np.cross(p2 - p1, p1 - np.asarray([p3.x, p3.y]))) / np.linalg.norm(p2 - p1) for p3 in
                    breaker.points])

        return dist

    def get_obj_value(self, domain, breakers):

        min_dist_to_fairway = min(
            [min([(self._dist_from_fairway_to_breaker(fairway, breaker)) for breaker in breakers])
             for
             fairway in
             domain.fairways])

        return -round(min_dist_to_fairway * 100, -1)


class WaveHeightObjective(Objective):

    def get_obj_value(self, domain, breakers, simulation_result: WaveSimulationResult):
        hs_vals = simulation_result.get_output_for_target_points(domain.target_points)

        hs_vals = [hs if hs > 0.01 else 9 for hs in hs_vals]

        hs_weigtened = [hs * pt.weight for hs, pt in zip(hs_vals, domain.target_points)]

        return [round((hs + 0.05) * 100, -1) for hs in hs_weigtened]  # to avoid zero


class WaveHeightMultivariateObjective(Objective):

    def get_obj_value(self, domain, breakers, simulation_result: WaveSimulationResult):
        hs_vals = simulation_result.get_output_for_target_points(domain.target_points)

        hs_weigtened = [hs * pt.weight for hs, pt in zip(hs_vals, domain.target_points)]

        return [round((hs + 0.05) * 100, -1) for hs in hs_weigtened]  # to avoid zero
