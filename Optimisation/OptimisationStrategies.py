import abc
from Breakers.Breaker import Breaker_descr, xy_to_points, Breaker


class OptimisationResults(object):
    def __init__(self, simulation_result, modifications, history):
        self.simulation_result = simulation_result
        self.modifications = modifications
        self.history = history


class OptimisationStrategyAbstract(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def optimise(self, model, construction_indexes):
        return


class EmptyOptimisationStrategy(OptimisationStrategyAbstract):
    def optimise(self, model):
        manual_modifications = {
            'mod1': Breaker_descr(list(map(xy_to_points, [[30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
            'mod2': Breaker_descr(list(map(xy_to_points, [[24, 16], [33, 22], [42, 17]])), 0, 'Ia'),
            'mod12': Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
            'mod26': Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),
        }

        modifications = [Breaker(_, manual_modifications[_]) for _ in ['mod1', 'mod12', 'mod26']]

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, modifications)

        return OptimisationResults(simulation_result, modifications, [])


class ManualOptimisationStrategy(OptimisationStrategyAbstract):
    def optimise(self, model):
        manual_modifications = {
            'mod1': Breaker_descr(list(map(xy_to_points, [[30, 20], [33, 22], [42, 17]])), 0, 'Ia'),
            'mod2': Breaker_descr(list(map(xy_to_points, [[24, 16], [33, 22], [42, 17]])), 0, 'Ia'),
            'mod12': Breaker_descr(list(map(xy_to_points, [[50, 24], [50, 32], [50, 39]])), 0, 'II'),
            'mod26': Breaker_descr(list(map(xy_to_points, [[56, 40], [56, 38]])), 0, '-'),
        }

        modifications = [Breaker(_, manual_modifications[_]) for _ in ['mod1', 'mod12', 'mod26']]

        # TODO: run all combinations and find best

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, modifications)

        return OptimisationResults(simulation_result, modifications, [])


class DifferentialOptimisationStrategy(OptimisationStrategyAbstract):
    def optimise(self, model):
        # TODO implement deoptim

        evolutionarty_modifications = []  # TODO fill

        best_modifications_ids = []  # TODO best indiviual

        modifications = [Breaker(_, evolutionarty_modifications[_]) for _ in [best_modifications_ids]]

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, modifications)

        return OptimisationResults(simulation_result, modifications, [])
