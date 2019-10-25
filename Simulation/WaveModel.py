import uuid
from multiprocessing import Lock

import pickledb

from Breakers.BreakersUtils import BreakersUtils
from Computation.СomputationalEnvironment import SwanComputationalManager, ComputationalManager
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Simulation.ConfigurationStrategies import GeomConfigurationStrategy, ConfigFileConfigurationStrategy, \
    ConfigurationInfo
from Simulation.ModelingStrategies import SimpleGeomSimulationStrategy, SwanSimulationStrategy
from Simulation.Results import SimulationResult


class WaveModel(object):

    def __init__(self, domain, simulation_strategy, configuration_strategy,
                 computational_manager: ComputationalManager):
        self.domain = domain
        self._simulation_strategy = simulation_strategy
        self._configuration_strategy = configuration_strategy
        self.computational_manager = computational_manager

        self.expensive = False
        self.model_results_file_name = 'D:\SWAN_sochi\model_results.db'

    def run_simulation(self, configuration: ConfigurationInfo, computational_manager: ComputationalManager):
        return self._simulation_strategy.simulate(configuration, computational_manager)

    def configurate(self, modifications, configuration_label: str):
        return self._configuration_strategy.configurate(self.domain, modifications, configuration_label)

    def run_simulation_for_constructions(self, modifications, forced_label=None) -> SimulationResult:

        if forced_label is None:
            configuration_label = uuid.uuid4().hex
        else:
            configuration_label = forced_label

        if self.expensive:
            serialised_breakers = BreakersEvoUtils.generate_genotype_from_breakers(modifications)

            if forced_label is None:
                loaded_configuration_reference = self._load_simulation_result_reference(serialised_breakers)
            else:
                loaded_configuration_reference = None

            if loaded_configuration_reference is None:
                configuration_info = self.configurate(modifications, configuration_label)
                results = self.run_simulation(configuration_info, computational_manager=self.computational_manager)
                if not forced_label:
                    self._save_simulation_result_reference(serialised_breakers,
                                                           configuration_label)
            else:
                print("Historical SWAN found")
                configuration_label = loaded_configuration_reference
                all_breakers = BreakersUtils.merge_breakers_with_modifications(self.domain.base_breakers, modifications)
                results = self.run_simulation(
                    ConfigurationInfo(all_breakers, self.domain, configuration_label, file_name=None),
                    computational_manager=self.computational_manager)
        else:
            configuration_info = self.configurate(modifications, configuration_label)
            results = self.run_simulation(configuration_info, computational_manager=None)

        return results

    def _save_simulation_result_reference(self, serialised_breakers, configuration_label: str):
        lock = Lock()
        lock.acquire()
        try:
            db = pickledb.load(self.model_results_file_name, False)
            db.set(serialised_breakers, configuration_label)
            db.dump()
        finally:
            lock.release()

    def _load_simulation_result_reference(self, serialised_breakers):
        db = pickledb.load(self.model_results_file_name, False)
        responce = db.get(serialised_breakers)
        if responce == False:
            return None
        configuration_label = responce
        return configuration_label

    def _load_simulation_result_reference_by_id(self, id):
        db = pickledb.load(self.model_results_file_name, False)
        for key in db.db:
            if db.db[key] == id:
                #print(key)
                return key
        return None


class SimpleGeomWaveModel(WaveModel):

    def __init__(self, domain):
        sim_strategy = SimpleGeomSimulationStrategy()
        conf_strategy = GeomConfigurationStrategy()

        super(SimpleGeomWaveModel, self).__init__(domain, sim_strategy, conf_strategy, None)


class SwanWaveModel(WaveModel):

    def __init__(self, domain, computational_manager: SwanComputationalManager):
        sim_strategy = SwanSimulationStrategy()
        conf_strategy = ConfigFileConfigurationStrategy()

        super(SwanWaveModel, self).__init__(domain, sim_strategy, conf_strategy, computational_manager)

        self.expensive = True
