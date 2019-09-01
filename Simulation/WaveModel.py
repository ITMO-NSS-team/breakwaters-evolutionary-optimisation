import uuid

import pickledb

from Breakers.BreakersUtils import BreakersUtils
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Simulation.ConfigurationStrategies import GeomConfigurationStrategy, ConfigFileConfigurationStrategy, \
    ConfigurationInfo
from Simulation.ModelingStrategies import SimpleGeomSimulationStrategy, SwanSimulationStrategy
from Simulation.Results import SimulationResult
from Computation.СomputationalEnvironment import SwanComputationalManager, ComputationalManager


class WaveModel(object):

    def __init__(self, domain, simulation_strategy, configuration_strategy, computational_manager):
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

    def run_simulation_for_constructions(self, base_breakers, modifications) -> SimulationResult:
        configuration_label = uuid.uuid4().hex

        if self.expensive:
            serialised_breakers = BreakersEvoUtils.generate_genotype_from_breakers(modifications)

            loaded_configuration_reference = self._load_simulation_result_reference(serialised_breakers)

            if loaded_configuration_reference is None:
                configuration_info = self.configurate(modifications, configuration_label)
                results = self.run_simulation(configuration_info, computational_manager=self.computational_manager)
                self._save_simulation_result_reference(serialised_breakers,
                                                       configuration_label)
            else:
                print("Historical SWAN found")
                configuration_label = loaded_configuration_reference
                all_breakers = BreakersUtils.merge_breakers_with_modifications(base_breakers, modifications)
                results = self.run_simulation(
                    ConfigurationInfo(all_breakers, self.domain, configuration_label, file_name=None),
                    computational_manager=None)
        else:
            configuration_info = self.configurate(modifications, configuration_label)
            results = self.run_simulation(configuration_info, computational_manager=None)

        return results

    def _save_simulation_result_reference(self, serialised_breakers, configuration_label: str):
        db = pickledb.load(self.model_results_file_name, False)
        db.set(serialised_breakers, configuration_label)
        db.dump()

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
            if db.db[key]==id:
                print(key)
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
