from abc import abstractmethod
from typing import List

import numpy as np
from shapely.geometry import LineString

from Breakers.Breaker import Breaker
from Configuration.Domains import Domain, Fairway
from Simulation.Results import WaveSimulationResult


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
        return round(cost, 0)


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
        hs_vals = simulation_result.get_5percent_output_for_target_points(domain.target_points)

        hs_vals = [hs if hs > 0.05 else 9 for hs in hs_vals]

        hs_weigtened = [hs * pt.weight for hs, pt in zip(hs_vals, domain.target_points)]

        return [round(hs * 100, -1) for hs in hs_weigtened]  # to avoid zero


class RelativeQuailityObjective(Objective):
    def get_obj_value(self, domain, breakers, base_breakers, simulation_result: WaveSimulationResult,
                      simulation_result_base: WaveSimulationResult):
        cost_obj_new = CostObjective().get_obj_value(domain, breakers)
        cost_obj_base = CostObjective().get_obj_value(domain, base_breakers)

        rel_cost_obj = ((cost_obj_new - cost_obj_base) / cost_obj_base) * 100

        wh_obj_new = WaveHeightObjective().get_obj_value(domain, breakers, simulation_result)
        wh_obj_old = WaveHeightObjective().get_obj_value(domain, base_breakers, simulation_result_base)

        rel_wh_obj = [(x1 - x2) / x2 * 100 for (x1, x2) in zip(wh_obj_new, wh_obj_old)]

        relative_quality_obj_value = (100 + np.mean(rel_wh_obj)) / (100 + rel_cost_obj)
        print(
            f'{relative_quality_obj_value},{rel_wh_obj},{rel_cost_obj},{cost_obj_new},{cost_obj_base},{wh_obj_new},{cost_obj_base}')
        return relative_quality_obj_value * 100
