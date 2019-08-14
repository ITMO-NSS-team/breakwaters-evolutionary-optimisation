import abc
import numpy as np


class WaveModel:

    def __init__(self, domain):
        self.domain = domain

    @abc.abstractmethod
    def run_simulation_for_constructions(self):
        return


class WaveSimulationResult:
    def __init__(self, hs):
        self.hs = hs

    def get_hs_for_target_point(self, point):
        return self.hs[point.x, point.y]


class SimpleGeomWaveModel(WaveModel):
    constructions_indexes = []

    def run_simulation_for_constructions(self, constructions_indexes):
        hs = np.zeros(shape=(self.domain.model_grid.grid_x, self.domain.model_grid.grid_y))

        # represent constructions

        # do math

        return WaveSimulationResult(hs)
