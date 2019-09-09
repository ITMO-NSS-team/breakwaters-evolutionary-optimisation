from abc import ABCMeta, abstractmethod


class SimulationResult(object):

    @abstractmethod
    def get_output_for_target_points(self, points):
        return


class WaveSimulationResult(SimulationResult):
    def __init__(self, hs, configuration_label):
        self.hs = hs
        # TODO move to parent
        self.configuration_label = configuration_label

    def _get_output_for_target_points(self, points):
        if isinstance(points, list):
            return [self.hs[point.y, point.x] for point in points]
        else:
            return self.hs[points.y, points.x]

    def get_5percent_output_for_target_points(self, points):
        hs = self._get_output_for_target_points(points)
        if isinstance(points, list):
            return [hs_i * 1.22 for hs_i in hs]
        else:
            return hs * 1.22

    def get_hs_output_for_target_points(self, points):
        return self._get_output_for_target_points(points)
