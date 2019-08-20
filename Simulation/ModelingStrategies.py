from abc import ABCMeta, abstractmethod
import numpy as np
import os
from Simulation.Results import WaveSimulationResult
from Simulation.ConfigurationStrategies import ConfigurationInfo


class SimulationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def simulate(self, configuration_info: ConfigurationInfo):
        return


class SimpleGeomSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):
        hs = np.zeros(shape=(configuration_info.domain.model_grid.grid_y, configuration_info.domain.model_grid.grid_x))

        # represent constructions

        # do math

        return WaveSimulationResult(hs)


class SwanSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):
        if not os.path.isfile(
                'D:\\SWAN_sochi\\r\\hs{}.d'.format(configuration_info.configuration_label)):
            print("SWAN RUNNED")
            os.system(r'swanrun.bat {}'.format(configuration_info.info))
            NotImplementedError
            print("SWAN FINISHED")
        #else:
            #print("FILE {} EXISTS".format(configuration_info.configuration_label))


        hs = np.genfromtxt('D:\\SWAN_sochi\\r\\hs{}.d'.format(configuration_info.configuration_label))

        return WaveSimulationResult(hs)
