from abc import ABCMeta, abstractmethod
import numpy as np
import os
from Simulation.Results import WaveSimulationResult
from Simulation.ConfigurationStrategies import ConfigurationInfo


class SimulationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def simulate(self, configuration_info: ConfigurationInfo):
        return


class PrimitiveGeomSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):
        hs = np.zeros(shape=(configuration_info.domain.model_grid.grid_x, configuration_info.domain.model_grid.grid_y))



        return WaveSimulationResult(hs)


class SimpleGeomSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):
        hs = np.zeros(shape=(configuration_info.domain.model_grid.grid_x, configuration_info.domain.model_grid.grid_y))

        # represent constructions

        # do math

        return WaveSimulationResult(hs)


class SwanSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):
        os.system(r'swanrun.bat {}'.format(configuration_info.info))

        hs = np.zeros(shape=(configuration_info.model_grid.grid_x, configuration_info.model_grid.grid_y))

        return hs
