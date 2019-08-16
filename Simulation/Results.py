from abc import ABCMeta, abstractmethod


class SimulationResult(object):
    @abstractmethod
    def get_output_for_target_point(self, point):
        return


class WaveSimulationResult(SimulationResult):
    def __init__(self, hs):
        self.hs = hs

    def get_output_for_target_point(self, point):
        return self.hs[point.x, point.y]
