import abc
import numpy as np
import sys
import fileinput
import re
import os
import shutil
import time
from Breakers.Obstacler import Obstacler


class ConfigurationInfo(object):
    def __init__(self, info, domain):
        self.info = info
        self.domain = domain


class ConfigurationStrategyAbstract(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def configurate(self, domain, constructions_data):
        return

    @abc.abstractmethod
    def build_constructions(self, model_grid, base_breakers, modifications):
        return


class GeomConfigurationStrategy(ConfigurationStrategyAbstract):
    def configurate(self, domain, constructions_data):
        return ConfigurationInfo(constructions_data, domain)

    def build_constructions(self, model_grid, base_breakers, modifications):
        obstacler = Obstacler(model_grid, index_mode=True)
        return obstacler.get_obstacle_for_modification(base_breakers, modifications)


class ConfigFileConfigurationStrategy(ConfigurationStrategyAbstract):
    def configurate(self, domain, constructions_data):
        out_file_name = 'HSign_snip_obst_obs_onlywind'
        base_name = 'CONFIG_opt.swn'
        os.chdir('D:\\SWAN_sochi\\')

        for i, line in enumerate(fileinput.input(base_name, inplace=1)):
            if 'optline' in line:
                for obs_str in constructions_data:
                    sys.stdout.write('{}\n'.format(obs_str))
                sys.stdout.write('$optline\n')
            elif 'OBSTACLE' in line:
                sys.stdout.write('')
            elif out_file_name in line:
                sys.stdout.write(
                    re.sub(r'{}.*.dat'.format(out_file_name), '{}_id{}.dat'.format(self.out_file_name, id), line))
            else:
                sys.stdout.write(line)

        time.sleep(2)
        new_config_name = 'CONFIG_opt_id{}.swn'.format(id)
        time.sleep(2)
        shutil.copy(base_name, new_config_name)
        time.sleep(2)

        return ConfigurationInfo(new_config_name, domain)

    def build_constructions(self, model_grid, base_breakers, modifications):
        obstacler = Obstacler(model_grid, index_mode=False)
        return obstacler.get_obstacle_for_modification(base_breakers, modifications)
