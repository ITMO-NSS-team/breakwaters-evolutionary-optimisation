from Simulation.ModelingStrategies import SimpleGeomSimulationStrategy, SwanSimulationStrategy
from Simulation.ConfigurationStrategies import GeomConfigurationStrategy, ConfigFileConfigurationStrategy


class WaveModel(object):

    def __init__(self, domain, simulation_strategy, configuration_strategy):
        self.domain = domain
        self._simulation_strategy = simulation_strategy
        self._configuration_strategy = configuration_strategy
        self.expensive = False

    def run_simulation(self, configuration):
        return self._simulation_strategy.simulate(configuration)

    def configurate(self, base_breakers, modifications, configuration_label):
        constructions = self._configuration_strategy.build_constructions(self.domain.model_grid, base_breakers, modifications)
        return self._configuration_strategy.configurate(self.domain, constructions, configuration_label)

    def run_simulation_for_constructions(self, base_breakers, modifications, configuration_label):

        configuration_info = self.configurate(base_breakers, modifications, configuration_label)
        results = self.run_simulation(configuration_info)
        return results


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

