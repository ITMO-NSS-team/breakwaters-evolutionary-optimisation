from abc import ABCMeta, abstractmethod
import numpy as np
import sys
import fileinput
import re
import os
import shutil
import time
import uuid

from Breakers.Obstacler import Obstacler


class ConfigurationInfo(object):
    def __init__(self, info, domain, label):
        self.info = info
        self.domain = domain
        self.configuration_label = label


class ConfigurationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def configurate(self, domain, constructions_data, configuration_label):
        return

    @abstractmethod
    def build_constructions(self, model_grid, base_breakers, modifications):
        return


class GeomConfigurationStrategy(ConfigurationStrategyAbstract):
    def configurate(self, domain, constructions_data, configuration_label):
        return ConfigurationInfo(constructions_data, domain, configuration_label)

    def build_constructions(self, model_grid, base_breakers, modifications):
        obstacler = Obstacler(model_grid, index_mode=True)
        return obstacler.get_obstacle_for_modification(base_breakers, modifications)


class ConfigFileConfigurationStrategy(ConfigurationStrategyAbstract):
    def configurate(self, domain, constructions_data, configuration_label):
        out_file_name = 'hs'
        base_name = 'CONFIG_opt.swn'
        os.chdir('D:\\SWAN_sochi\\')

        if not os.path.isfile(
                f'D:\\SWAN_sochi\\r\\hs{configuration_label}.d'):

            for i, line in enumerate(fileinput.input(base_name, inplace=1)):
                if 'optline' in line:
                    for obs_str in constructions_data:
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

        return ConfigurationInfo(new_config_name, domain, configuration_label)

    def build_constructions(self, model_grid, base_breakers, modifications):
        obstacler = Obstacler(model_grid, index_mode=False)
        return obstacler.get_obstacle_for_modification(base_breakers, modifications)
