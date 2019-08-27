import fileinput
import os
import re
import shutil
import sys
import time
from abc import ABCMeta, abstractmethod

import numpy as np


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