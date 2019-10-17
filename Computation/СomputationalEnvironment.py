import json
from abc import abstractmethod

import winrm  # install as pip install pywinrm==0.2.2
import shutil
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
from multiprocessing import Lock

'''
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
net start WinRM
powershell enable - psremoting - force
exit
winrm get winrm/config
winrm set winrm/config/service/auth @{Basic="true"}
winrm set winrm/config/service @{AllowUnencrypted="true"}
'''


class ComputationalResourceDescription(object):
    def __init__(self, resources_config_name):
        if os.path.isfile(resources_config_name):
            config_file = open(resources_config_name)
            json_str = config_file.read()
            self.config_dict = json.loads(json_str)
        else:
            self.config_dict = None


class ComputationalManager(object):
    def __init__(self, resources_names, is_lazy_parallel=False):
        self.resources_names = resources_names
        self.resources_description = ComputationalResourceDescription("remotes_config.json")
        assert self.resources_description.config_dict is not None

        if self.resources_description.config_dict is not None:
            self.resources_description = [desc for desc in self.resources_description.config_dict if
                                          desc['name'] in resources_names]

            for rd in self.resources_description:
                rd["is_free"] = True

        self.is_lazy_parallel = is_lazy_parallel

    @abstractmethod
    def execute(self, config_file_name, out_file_name):
        return

    @abstractmethod
    def finalise_execution(self):
        return


class SwanComputationalManager(ComputationalManager):
    @abstractmethod
    def execute(self, config_file_name, out_file_name):
        return


# TODO implement as strategy pattern
class SwanWinRemoteComputationalManager(SwanComputationalManager):
    def __init__(self, resources_names, is_lazy_parallel=False):
        self.input_data = []

        super(SwanWinRemoteComputationalManager, self).__init__(resources_names, is_lazy_parallel)

        self.runned = False

    def _execute_single(self, input_data):
        config_file_name, out_file_name = input_data

        if config_file_name is not None:  # if new calculacation reqired
            lock = Lock()
            lock.acquire()
            try:
                cur_res_index = -1
                for rd_ind, rd in enumerate(self.resources_description):
                    # print(rd["name"])
                    if rd["is_free"]:
                        cur_res_index = rd_ind
                        self.resources_description[cur_res_index]["is_free"] = False
                        resource_description = rd
                        break
            finally:
                lock.release()

            print("task sent to the {server_name}".format(server_name=resource_description["name"]))
            # from local SWAN to share
            shutil.copy(f'D:\\SWAN_sochi\\{config_file_name}.swn', resource_description["transfer_folder_localname"])

            transfer_folder = resource_description[
                'transfer_folder']  # '\\\\192.168.13.1\\share\share_with_blades\\125'

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
            # print(out)

            shutil.copy(resource_description['transfer_folder_localname'] + f"//{out_file_name}", "D:\\SWAN_sochi\\r")

            self.resources_description[cur_res_index]["is_free"] = True

        return out_file_name[2:(len(out_file_name) - 2)]

    def execute(self, config_file_name, out_file_name):
        if self.resources_description is None:
            FileNotFoundError("Remote configuration config not found")

        if self.is_lazy_parallel:
            self.input_data.append((config_file_name, out_file_name))
        else:
            self._execute_single((config_file_name, out_file_name))
        return

    def finalise_execution(self):
        # print('finalise_execution')
        results_list = []
        # TODO check order
        if len(self.input_data) > 0:
            workers_num = len(self.resources_description)
            with ThreadPoolExecutor(max_workers=workers_num) as executor:
                for file in executor.map(self._execute_single, self.input_data):
                    hs = np.genfromtxt(f'D:\\SWAN_sochi\\r\\hs{file}.d')
                    lock = Lock()
                    lock.acquire()
                    try:
                        results_list.append((file, hs))
                    finally:
                        lock.release()
            self.input_data = []
        return results_list