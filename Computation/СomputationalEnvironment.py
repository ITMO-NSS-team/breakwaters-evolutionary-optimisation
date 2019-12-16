import json
import os
import shutil
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Lock
import subprocess
from CommonUtils.StaticStorage import StaticStorage

import numpy as np
import winrm  # install as pip install pywinrm==0.2.2

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
    def __init__(self, resources_names):
        self.resources_names = resources_names
        self.resources_description = ComputationalResourceDescription("remotes_config.json")
        self.input_data = []

        assert self.resources_description.config_dict is not None

        if self.resources_description.config_dict is not None:
            self.resources_description = [desc for desc in self.resources_description.config_dict if
                                          desc['name'] in resources_names]

            for rd in self.resources_description:
                rd["is_free"] = True

    @abstractmethod
    def execute(self, config_file_name, out_file_name):
        return

    @abstractmethod
    def finalise_execution(self):
        return


class SwanComputationalManager(ComputationalManager):
    def execute(self, config_file_name, out_file_name):
        if self.resources_description is None:
            FileNotFoundError("Computational config not found")
        self.input_data.append((config_file_name, out_file_name))
        return

    def prepare_simulations_for_population(self, population, model):
        pre_simulated_results = []
        pre_simulated_results_idx = []

        for individual_ind, individual in enumerate(population):
            simulation_result = model.run_simulation_for_constructions(individual.genotype.get_genotype_as_breakers())

            pre_simulated_results.append(simulation_result)
            pre_simulated_results_idx.append(simulation_result.configuration_label)

        base_simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers)
        pre_simulated_results.append(base_simulation_result)
        pre_simulated_results_idx.append(base_simulation_result.configuration_label)

        finalised_values = model.computational_manager.finalise_execution()

        if len(finalised_values) > 0:
            for i, val in enumerate(finalised_values):
                label = val[0]
                hs = val[1]
                indices = [i for i, x in enumerate(pre_simulated_results_idx) if x == label]
                if len(indices) > 2:
                    print("STRANGE")
                for idx in indices:
                    pre_simulated_results[idx]._hs = hs

        for ps in pre_simulated_results:
            if ps._hs is None:
                print("NONE FOUND")
        return pre_simulated_results


# TODO implement as strategy pattern
class SwanWinRemoteComputationalManager(SwanComputationalManager):
    def __init__(self, resources_names):
        super(SwanWinRemoteComputationalManager, self).__init__(resources_names)

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

            if StaticStorage.is_verbose:
                print("task sent to the {server_name}".format(server_name=resource_description["name"]))

            # from local SWAN to share
            shutil.copy(f'D:\\SWAN_sochi\\{config_file_name}.swn', resource_description["transfer_folder_localname"])
            if StaticStorage.remove_tmp:
                os.remove(f'D:\\SWAN_sochi\\{config_file_name}.swn')

            transfer_folder = resource_description[
                'transfer_folder']

            config_name = config_file_name

            swan_remote_path = resource_description['remote_model_folder']

            ps_script_1 = r"""Copy-Item %s\%s.swn %s
                        """ % (transfer_folder, config_name, swan_remote_path)

            ps_script_2 = r"""& %s\swanrun.bat %s\\%s
                        """ % (swan_remote_path, swan_remote_path, config_name)

            swan_remote_path_results = '%s\\r' % swan_remote_path
            result_name = out_file_name  # 'HSign_v0.dat'
            ps_script_3 = r"""Copy-Item  %s\\%s %s
                        """ % (swan_remote_path_results, result_name, transfer_folder)

            ps_script_4 = r"""Remove-Item %s\\%s.swn
                        """ % (swan_remote_path, config_name)

            ps_script_5 = r"""Remove-Item %s\\%s
                        """ % (swan_remote_path_results, result_name)

            ps_script_6 = r"""Remove-Item %s\\%s.prt
                        """ % (swan_remote_path, config_name)

            if StaticStorage.remove_tmp:
                script = ps_script_1 + ps_script_2 + ps_script_3 + ps_script_4 + ps_script_5 + ps_script_6
            else:
                script = ps_script_1 + ps_script_2 + ps_script_3

            s = winrm.Session(resource_description['url'],
                              auth=(resource_description['login'], resource_description['password']))

            res = s.run_ps(script)

            # remove config from transfer folder
            rem_cnf_name = resource_description["transfer_folder_localname"] + '//{config_file_name}.swn'
            if StaticStorage.remove_tmp and os.path.exists(rem_cnf_name):
                os.remove(rem_cnf_name)

            shutil.copy(resource_description['transfer_folder_localname'] + f"//{out_file_name}", "D:\\SWAN_sochi\\r")

            # remove results from transfer folder
            tra_res_name = resource_description['transfer_folder_localname'] + f"//{out_file_name}"
            if StaticStorage.remove_tmp and os.path.exists(tra_res_name):
                os.remove(tra_res_name)

            self.resources_description[cur_res_index]["is_free"] = True

        return out_file_name[2:(len(out_file_name) - 2)]

    def finalise_execution(self):
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


class SwanWinLocalComputationalManager(SwanComputationalManager):
    def __init__(self):
        super(SwanWinLocalComputationalManager, self).__init__("local")

    def finalise_execution(self):
        results_list = []
        # TODO check order
        if len(self.input_data) > 0:
            for file in map(self._execute_single, self.input_data):
                hs = np.genfromtxt(f'D:\\SWAN_sochi\\r\\hs{file}.d')
                results_list.append((file, hs))
            self.input_data = []
        return results_list

    def _execute_single(self, input_data):
        config_file_name, out_file_name = input_data

        if config_file_name is not None:  # if new calculacation reqired
            model_folder = self.resources_description[0]["remote_model_folder"]

            if not os.path.isfile(f'{model_folder}\\r\\{out_file_name}'):
                saved_work_dir = os.getcwd()
                os.chdir(model_folder)
                if StaticStorage.is_verbose:
                    subprocess.run(fr'swanrun.bat {config_file_name} ', shell=True)
                else:
                    subprocess.run(fr'swanrun.bat {config_file_name} ', shell=True, stdout=subprocess.DEVNULL)

                if StaticStorage.remove_tmp:
                    # remove configuration file
                    cnf_name = f'{model_folder}\\{config_file_name}.swn'
                    if os.path.exists(cnf_name):
                        os.remove(cnf_name)
                    # remove log file
                    tmp_name = f'{model_folder}\\{config_file_name}.prt'
                    if os.path.exists(tmp_name): os.remove(tmp_name)

                os.chdir(saved_work_dir)
            if StaticStorage.is_verbose:
                print("task sent to the {server_name}".format(server_name=self.resource_description["name"]))
        return out_file_name[2:(len(out_file_name) - 2)]
