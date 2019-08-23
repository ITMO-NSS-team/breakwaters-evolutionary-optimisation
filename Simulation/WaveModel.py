import uuid

import pickledb

from Breakers.BreakersUtils import BreakersUtils
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from Simulation.ConfigurationStrategies import GeomConfigurationStrategy, ConfigFileConfigurationStrategy, \
    ConfigurationInfo
from Simulation.ModelingStrategies import SimpleGeomSimulationStrategy, SwanSimulationStrategy


class WaveModel(object):

    def __init__(self, domain, simulation_strategy, configuration_strategy):
        self.domain = domain
        self._simulation_strategy = simulation_strategy
        self._configuration_strategy = configuration_strategy
        self.expensive = False
        self.model_results_file_name = 'D:\SWAN_sochi\model_results.db'

    def run_simulation(self, configuration):
        return self._simulation_strategy.simulate(configuration)

    def configurate(self, modifications, configuration_label):
        return self._configuration_strategy.configurate(self.domain, modifications, configuration_label)

    def run_simulation_for_constructions(self, base_breakers, modifications):
        configuration_label = uuid.uuid4().hex

        if self.expensive:
            serialised_breakers = BreakersEvoUtils.generate_genotype_from_breakers(modifications)

            loaded_configuration_reference = self._load_simulation_result_reference(serialised_breakers)

            if loaded_configuration_reference is None:
                configuration_info = self.configurate(modifications, configuration_label)
                results = self.run_simulation(configuration_info)
                self._save_simulation_result_reference(serialised_breakers,
                                                       configuration_label)
            else:
                configuration_label = loaded_configuration_reference
                all_breakers = BreakersUtils.merge_breakers_with_modifications(base_breakers, modifications)
                results = self.run_simulation(
                    ConfigurationInfo(all_breakers, self.domain, configuration_label, file_name=None))
        else:
            configuration_info = self.configurate(modifications, configuration_label)
            results = self.run_simulation(configuration_info)

        return results

    def _save_simulation_result_reference(self, serialised_breakers, configuration_label):
        db = pickledb.load(self.model_results_file_name, False)
        db.set(serialised_breakers, configuration_label)
        db.dump()

    def _load_simulation_result_reference(self, serialised_breakers):
        db = pickledb.load(self.model_results_file_name, False)
        configuration_label = db.get(serialised_breakers)
        if configuration_label == False:
            return None
        return configuration_label


class SimpleGeomWaveModel(WaveModel):

    def __init__(self, domain):
        sim_strategy = SimpleGeomSimulationStrategy()
        conf_strategy = GeomConfigurationStrategy()

        super(SimpleGeomWaveModel, self).__init__(domain, sim_strategy, conf_strategy)


class SwanWaveModel(WaveModel):

    def __init__(self, domain):
        sim_strategy = SwanSimulationStrategy()
        conf_strategy = ConfigFileConfigurationStrategy()

        super(SwanWaveModel, self).__init__(domain, sim_strategy, conf_strategy)

        self.expensive = True
