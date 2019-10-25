from abc import ABCMeta, abstractmethod
from copy import copy


class SimulationResult(object):

    @abstractmethod
    def _get_output_for_target_points(self, points):
        return


class WaveSimulationResult(SimulationResult):

    def __init__(self, hs, configuration_label):
        self._hs = copy(hs)
        # TODO move to parent
        self.configuration_label = configuration_label

        self.coeff_hs_to_5 = 1.22
        self.coeff_5_to_mean = 1.81

    def _get_output_for_target_points(self, points):
        if isinstance(points, list):
            return [self._hs[point.y, point.x] for point in points]
        else:
            return self._hs[points.y, points.x]

    def get_5percent_output_for_target_points(self, points):
        hs = self._get_output_for_target_points(points)
        if isinstance(points, list):
            return [hs_i * self.coeff_hs_to_5 for hs_i in hs]
        else:
            return hs * self.coeff_hs_to_5

    def get_mean_output_for_target_points(self, points):
        hs = self._get_output_for_target_points(points)
        if isinstance(points, list):
            return [hs_i * self.coeff_hs_to_5 * self.coeff_5_to_mean for hs_i in hs]
        else:
            return hs * self.coeff_hs_to_5 / self.coeff_5_to_mean

    def get_13percent_output_for_target_points(self, points):
        return self._get_output_for_target_points(points)

    def get_5percent_output_for_field(self):
        hs = copy(self._hs)
        hs[hs != -9] = hs[hs != -9] * self.coeff_hs_to_5
        return hs

    def get_mean_output_for_field(self):
        hs = copy(self._hs)
        hs[hs != -9] = hs[hs != -9] * self.coeff_hs_to_5 / self.coeff_5_to_mean

        return hs
