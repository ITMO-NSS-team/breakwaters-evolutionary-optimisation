import os
import re
from abc import ABCMeta, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
from sympy import Line, Point, Segment, intersection

from Simulation.ConfigurationStrategies import ConfigurationInfo
from Visualisation.ModelVisualization import ModelsVisualization
from Simulation.Results import WaveSimulationResult
from Computation.СomputationalEnvironment import SwanComputationalManager, ComputationalManager
from CommonUtils.StaticStorage import StaticStorage


class SimulationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def simulate(self, configuration_info: ConfigurationInfo, computational_manager: ComputationalManager):
        return


class SwanSimulationStrategy(SimulationStrategyAbstract):

    def simulate(self, configuration_info: ConfigurationInfo, computational_manager: SwanComputationalManager,
                 output_time_step):

        out_file_name = f'hs{configuration_info.configuration_label}.d'

        if os.path.isfile('D:\\SWAN_sochi\\r\\hs{}.d'.format(configuration_info.configuration_label)):
            ts = output_time_step
            hs = np.genfromtxt(f'D:\\SWAN_sochi\\r\\{out_file_name}')
            start = (ts - 1) * configuration_info.domain.model_grid.grid_y
            end = ts * configuration_info.domain.model_grid.grid_y
            hs = hs[start:end]
        else:
            computational_manager.execute(configuration_info.file_name, out_file_name)
            hs = None

        return WaveSimulationResult(hs, configuration_info.configuration_label)
