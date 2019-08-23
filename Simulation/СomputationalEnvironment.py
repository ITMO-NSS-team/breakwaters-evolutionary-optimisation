import json
from abc import abstractmethod

import winrm
import shutil

from multiprocessing import Process


class ComputationalResourceDescription(object):
    def __init__(self, resources_config_name):
        config_file = open(resources_config_name)
        json_str = config_file.read()
        self.config_dict = json.loads(json_str)


class ComputationalManager(object):
    def __init__(self, resources_names):
        self.resources_names = resources_names
        self.resources_description = ComputationalResourceDescription("remotes_config.json")
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
        resource_description = self.resources_description[0]

        shutil.copy(f'D:\\SWAN_sochi\\{config_file_name}.swn', 'Z:/share_with_blades/125')
                    #resource_description['transfer_folder'])



        ps_script_1 = r"""Copy-Item {source}\\{config_file_name}.swn {target}
""".format(source=resource_description['transfer_folder'], target=resource_description['model_folder'],
                   config_file_name=config_file_name)

        ps_script_2 = r"""& {model_folder}swanrun.bat {config_name}.swn
""".format(model_folder=resource_description['model_folder'], config_name=config_file_name)

        ps_script_3 = r"""Copy-Item  {source}\\results\\{out_file_name} {target}
""".format(target=resource_description['transfer_folder'],
                   source=resource_description['model_folder'],
                   out_file_name=out_file_name)

        ps_script_1 = r"""Copy-Item \\192.168.13.1\share\Deeva\CONFIG_v0.{s} C:\\Users\\nano_user
        """.format(s="swn")

        ps_script_2 = r"""& D:\{SWAN}_sochi\swanrun.bat CONFIG_v0
        """.format(SWAN="SWAN")

        ps_script_3 = r"""Copy-Item  C:\\Users\\{nano_user}\\results\\HSign_v0.dat \\192.168.13.1\share\Deeva
        """.format(nano_user="nano_user")

        script = ps_script_1 + ps_script_2 + ps_script_3
        s = winrm.Session(resource_description['url'],
                          auth=(resource_description['login'], resource_description['password']))


        r1 = s.run_ps(script)

        out = r1.std_out
        print(out)
        print('end')

        shutil.copy(resource_description['transfer_folder'] + f"{out_file_name}", "D:\sim_results_storage")

        return
