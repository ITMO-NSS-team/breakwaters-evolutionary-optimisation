from abc import ABCMeta, abstractmethod


class SimulationResult(object):
    @abstractmethod
    def get_output_for_target_points(self, points):
        return


class WaveSimulationResult(SimulationResult):
    def __init__(self, hs, configuration_label):
        self.hs = hs
        #TODO move to parent
        self.configuration_label = configuration_label

    def get_output_for_target_points(self, points):
        if isinstance(points, list):
            return [self.hs[point.y, point.x] for point in points]
        else:
            return self.hs[points.y, points.x]
