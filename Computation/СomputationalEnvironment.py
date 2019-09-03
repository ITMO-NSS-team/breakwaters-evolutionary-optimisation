import json
from abc import abstractmethod

import winrm  # install as pip install pywinrm==0.2.2
import shutil
import os

from multiprocessing import Process


class ComputationalResourceDescription(object):
    def __init__(self, resources_config_name):
        if os.path.isfile(resources_config_name):
            config_file = open(resources_config_name)
            json_str = config_file.read()
            self.config_dict = json.loads(json_str)
        else:
            self.config_dict = None


class ComputationalManager(object):
    def __init__(self, resources_names):
        self.resources_names = resources_names
        self.resources_description = ComputationalResourceDescription("remotes_config.json")
        if self.resources_description.config_dict is not None:
            self.resources_description = [desc for desc in self.resources_description.config_dict if
                                          desc['name'] in resources_names]

            for rd in self.resources_description:
                rd["is_free"] = True

    @abstractmethod
    def execute(self, config_file_name, out_file_name):
        return


class SwanComputationalManager(ComputationalManager):
    @abstractmethod
    def execute(self, config_file_name, out_file_name):
        return


# TODO implement as strategy pattern
class SwanWinRemoteComputationalManager(SwanComputationalManager):
    def execute(self, config_file_name, out_file_name):
        if self.resources_description is None:
            FileNotFoundError("Remote configuration config not found")
        resource_description = self.resources_description[0]

        # from local SWAN to share
        shutil.copy(f'D:\\SWAN_sochi\\{config_file_name}.swn', resource_description["transfer_folder_localname"])

        transfer_folder = resource_description['transfer_folder']  # '\\\\192.168.13.1\\share\share_with_blades\\125'

        config_name = config_file_name  # "CONFIG_v1"

        swan_remote_path = resource_description['remote_model_folder']  # 'C:\\Users\\nano_user'

        ps_script_1 = r"""Copy-Item %s\%s.swn %s
        """ % (transfer_folder, config_name, swan_remote_path)

        ps_script_2 = r"""& %s\swanrun.bat %s\\%s
        """ % (swan_remote_path, swan_remote_path, config_name)

        swan_remote_path_results = '%s\\r' % swan_remote_path
        result_name = out_file_name  # 'HSign_v0.dat'
        ps_script_3 = r"""Copy-Item  %s\\%s %s
        """ % (swan_remote_path_results, result_name, transfer_folder)

        script = ps_script_1 + ps_script_2 + ps_script_3
        s = winrm.Session(resource_description['url'],
                          auth=(resource_description['login'], resource_description['password']))

        r1 = s.run_ps(script)

        out = r1.std_out
        print(out)
        print('end')

        shutil.copy(resource_description['transfer_folder_localname'] + f"//{out_file_name}", "D:\\SWAN_sochi\\r")

        return
