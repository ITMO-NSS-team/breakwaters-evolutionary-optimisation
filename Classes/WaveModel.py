import abc
import numpy as np

import sys
import fileinput
import re
import os
import shutil
import time


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


class SwanWaveModel(WaveModel):
    constructions_obstacles = []

    out_file_name = 'HSign_snip_obst_obs_onlywind'
    base_name = 'CONFIG_opt.swn'

    def run_simulation_for_constructions(self, constructions_obstacles):

        os.chdir("D:\\SWAN_sochi\\")

        for i, line in enumerate(fileinput.input(self.base_name, inplace=1)):
            if 'optline' in line:
                for obs_str in constructions_obstacles:
                    sys.stdout.write('{}\n'.format(obs_str))
                sys.stdout.write('$optline\n')
            elif 'OBSTACLE' in line:
                sys.stdout.write('')
            elif self.out_file_name in line:
                sys.stdout.write(
                    re.sub(r'{}.*.dat'.format(self.out_file_name), '{}_id{}.dat'.format(self.out_file_name, id), line))
            else:
                sys.stdout.write(line)
        time.sleep(2)
        newConfigName = "CONFIG_opt_id{}.swn".format(id)
        time.sleep(2)
        shutil.copy(self.base_name, newConfigName)
        time.sleep(2)
        os.system(r"swanrun.bat CONFIG_opt_id{}".format(id))

        hs = np.zeros(shape=(self.domain.model_grid.grid_x, self.domain.model_grid.grid_y))

        return hs
