import fileinput
import os
import re
import shutil
import sys
import time
from abc import ABCMeta, abstractmethod

import numpy as np

from Breakers.BreakersUtils import BreakersUtils


class ConfigurationInfo(object):
    def __init__(self, breakers, domain, label, file_name=None):
        self.breakers = breakers
        self.domain = domain
        self.configuration_label = label
        self.file_name = file_name


class ConfigurationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def configurate(self, domain, constructions_data, configuration_label):
        return


class GeomConfigurationStrategy(ConfigurationStrategyAbstract):

    def configurate(self, domain, modified_breakers, configuration_label):
        all_breakers = BreakersUtils.merge_breakers_with_modifications(domain.base_breakers, modified_breakers)
        return ConfigurationInfo(all_breakers, domain, configuration_label)


class ConfigFileConfigurationStrategy(ConfigurationStrategyAbstract):

    def _get_obstacle_for_modification(self, grid, base_breakers, modifications):
        final_obst = []
        all_modified_base_breakers_ids = []

        for modification in modifications:
            all_modified_base_breakers_ids.append(modification.base_id)
            final_obst.append(self._get_obst_for_breaker(grid, modification))

        all_modified_base_breakers = np.unique(all_modified_base_breakers_ids)

        for base_breaker in base_breakers:
            if all_modified_base_breakers != [] and base_breaker.breaker_id not in all_modified_base_breakers:
                final_obst.append(self._get_obst_for_breaker(grid, base_breaker))

        final_obst = np.unique(final_obst)
        return final_obst

    def _get_obst_for_breaker(self, grid, breaker):
        indices = breaker.points
        obs_str = 'OBSTACLE TRANSM 0. REFL {} LINE '.format(breaker.reflection)
        old_x = -10
        old_y = -10
        real_len = 0
        for i in range(0, len(indices)):
            p_cur = grid.get_coords_meter(breaker.points[i])
            new_x = int(round(p_cur[0]))
            new_y = int(round(p_cur[1]))
            if old_x == -10 or (new_x != old_x or new_y != old_y):
                obs_str += '{},{}'.format(new_x, new_y)
                if i != len(indices) - 1:
                    obs_str += ','
                real_len += 1
            old_x = new_x
            old_y = new_y
        if real_len > 1:
            return obs_str
        return ""

    def configurate(self, domain, modified_breakers, configuration_label):
        out_file_name = 'hs'
        base_name = 'CONFIG_opt.swn'

        saved_work_dir = os.getcwd()
        os.chdir('D:\\SWAN_sochi\\')

        if not os.path.isfile(
                f'D:\\SWAN_sochi\\r\\hs{configuration_label}.d'):

            all_obstacles = self._get_obstacle_for_modification(domain.model_grid, domain.base_breakers,
                                                                modified_breakers)
            all_breakers = BreakersUtils.merge_breakers_with_modifications(domain.base_breakers, modified_breakers)

            for i, line in enumerate(fileinput.input(base_name, inplace=1)):
                if 'optline' in line:
                    for obs_str in all_obstacles:
                        sys.stdout.write('{}\n'.format(obs_str))
                    sys.stdout.write('$optline\n')
                elif 'OBSTACLE' in line:
                    sys.stdout.write('')
                elif out_file_name in line:
                    sys.stdout.write(
                        re.sub(r'{}.*.d'.format(out_file_name), '{}{}.d'.format(out_file_name, configuration_label),
                               line))
                else:
                    sys.stdout.write(line)

            # time.sleep(2)
            new_config_name = 'CONFIG_opt_id{}'.format(configuration_label)
            new_config_full_name = '{}.swn'.format(new_config_name)
            time.sleep(2)
            shutil.copy(base_name, new_config_full_name)
            time.sleep(2)
        else:
            new_config_name = None

        os.chdir(saved_work_dir)

        return ConfigurationInfo(all_breakers, domain, configuration_label, new_config_name)

    def build_constructions(self, model_grid, base_breakers, modifications):
        return self._get_obstacle_for_modification(model_grid, base_breakers, modifications)
