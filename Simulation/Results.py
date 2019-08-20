from abc import ABCMeta, abstractmethod


class SimulationResult(object):
    @abstractmethod
    def get_output_for_target_points(self, points):
        return


class WaveSimulationResult(SimulationResult):
    def __init__(self, hs):
        self.hs = hs

    def get_output_for_target_points(self, points):
        if isinstance(points, list):
            return [self.hs[point.y, point.x] for point in points]
        else:
            return self.hs[points.y, points.x]
