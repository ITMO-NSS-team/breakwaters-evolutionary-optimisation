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
            return [self.hs[point.x, point.y] for point in points]
        else:
            return self.hs[points.x, points.y]
