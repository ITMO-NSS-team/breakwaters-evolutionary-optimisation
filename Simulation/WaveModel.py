from Simulation.ModelingStrategies import SimpleGeomSimulationStrategy, SwanSimulationStrategy
from Simulation.ConfigurationStrategies import GeomConfigurationStrategy, ConfigFileConfigurationStrategy


class WaveModel(object):

    def __init__(self, domain, simulation_strategy, configuration_strategy):
        self.domain = domain
        self._simulation_strategy = simulation_strategy
        self._configuration_strategy = configuration_strategy

    def run_simulation(self, configuration):
        return self._simulation_strategy.simulate(configuration)

    def configurate(self, constructions):
        return self._configuration_strategy.configurate(self.domain, constructions)

    def run_simulation_for_constructions(self, constructions):
        configuration_info = self.configurate(constructions)
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
