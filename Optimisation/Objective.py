from enum import Enum

import numpy as np
from shapely.geometry import LineString

from Breakers.Breaker import Breaker
from Configuration.Domains import Fairway
from Simulation.Results import WaveSimulationResult
from Breakers.BreakersUtils import BreakersUtils

class ConstraintComparisonType(Enum):
    not_equal = 0
    equal = 1
    less_or_equal = 2
    less = 3
    more_or_equal = 4
    more = 5


class ObjectiveData:
    def __init__(self, domain, proposed_breakers, base_breakers, simulation_result: WaveSimulationResult,
                 simulation_result_base: WaveSimulationResult):
        self.domain = domain
        self.base_breakers = base_breakers
        self.simulation_result_base = simulation_result_base

        if proposed_breakers is None and simulation_result is None:
            self.new_breakers = self.base_breakers
            self.simulation_result = self.simulation_result_base
        else:
            self.new_breakers = BreakersUtils.merge_breakers_with_modifications(base_breakers, proposed_breakers)
            self.simulation_result = simulation_result
        return

    def data_for_base_construction(self):
        return ObjectiveData(self.domain, None, self.base_breakers, None,
                             self.simulation_result_base)


class Objective(object):
    is_simulation_required = False

    def get_obj_value(self, obj_data: ObjectiveData):
        return


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

    def get_obj_value(self, obj_data):
        num_self_intersection = sum(
            [sum([int(self._selfintersection(breaker1, breaker2)) for breaker2 in obj_data.new_breakers]) for breaker1 in
             obj_data.new_breakers])

        return round(num_self_intersection * 100, -1)


class CostObjective(Objective):
    is_simulation_required = False

    def get_obj_value(self, obj_data):
        cost = sum([breaker.get_length() for breaker in obj_data.new_breakers]) * 25
        return round(cost, 0)


class RelativeCostObjective(CostObjective):
    def get_obj_value(self, obj_data):
        cost_obj_new = CostObjective().get_obj_value(obj_data)
        cost_obj_base = CostObjective().get_obj_value(obj_data.data_for_base_construction())
        cost_obj_rel = (cost_obj_new - cost_obj_base) / cost_obj_base * 100
        return cost_obj_rel


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

    def get_obj_value(self, obj_data):
        min_dist_to_fairway = min(
            [min([(self._dist_from_fairway_to_breaker(fairway, breaker)) for breaker in obj_data.new_breakers])
             for
             fairway in
             obj_data.domain.fairways])

        return -min_dist_to_fairway * 100


class RelativeNavigationObjective(NavigationObjective):
    is_simulation_required = False

    def get_obj_value(self, obj_data):
        nav_obj_new = NavigationObjective().get_obj_value(obj_data)
        nav_obj_base = NavigationObjective().get_obj_value(obj_data.data_for_base_construction())
        nav_obj_rel = (nav_obj_base - nav_obj_new) / nav_obj_base * 100

        if np.isnan(nav_obj_rel):
            nav_obj_rel = 0

        return nav_obj_rel

class WaveHeightObjective(Objective):
    is_simulation_required = True

    def get_obj_value(self, obj_data):
        hs_vals = obj_data.simulation_result.get_5percent_output_for_target_points(obj_data.domain.target_points)

        hs_vals = [hs if hs > 0.01 else 9 for hs in hs_vals]  # if model fails
        hs_vals = [hs if hs > 0.5 else 0.5 for hs in hs_vals]  # lower theshold

        return [round(hs * 100, -1) for hs in hs_vals]  # to avoid zero


class RelativeWaveHeightObjective(WaveHeightObjective):

    def get_obj_value(self, obj_data):
        wh_obj_new = WaveHeightObjective().get_obj_value(obj_data)
        wh_obj_base = WaveHeightObjective().get_obj_value(obj_data.data_for_base_construction())

        wh_obj_rel = [(x1 - x2) / x2 * 100 for (x1, x2) in zip(wh_obj_new, wh_obj_base)]

        return wh_obj_rel


class RelativeQuailityObjective(Objective):
    is_simulation_required = True

    def get_obj_value(self, obj_data):
        cost_obj_rel = RelativeCostObjective().get_obj_value(obj_data)
        wh_obj_real = RelativeWaveHeightObjective().get_obj_value(obj_data)

        relative_quality_obj_value = (100 + np.mean(wh_obj_real)) / (100 - cost_obj_rel)

        return relative_quality_obj_value * 100


class CompositeObjective(Objective):
    is_simulation_required = True

    def get_obj_value(self, obj_data):
        cost_obj_rel = RelativeCostObjective().get_obj_value(obj_data)
        nav_obj_rel = RelativeNavigationObjective().get_obj_value(obj_data)
        wh_obj_rel = RelativeWaveHeightObjective().get_obj_value(obj_data)

        composite_objective = sum(wh_obj_rel) * 2 + cost_obj_rel * 1 + nav_obj_rel * 0.5

        return composite_objective
