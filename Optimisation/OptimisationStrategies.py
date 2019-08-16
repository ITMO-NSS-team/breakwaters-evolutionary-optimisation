from abc import ABCMeta, abstractmethod
from Breakers.Breaker import Breaker
import numpy as np
from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objectives import *

from Simulation import WaveModel


class OptimisationResults(object):
    def __init__(self, simulation_result, modifications, history):
        self.simulation_result = simulation_result
        self.modifications = modifications
        self.history = history


class OptimisationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def optimise(self, model: WaveModel, task: OptimisationTask):
        return


class EmptyOptimisationStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask):
        modifications = task.possible_modifications

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, modifications)

        return OptimisationResults(simulation_result, modifications, [])


class ManualOptimisationStrategy(OptimisationStrategyAbstract):
    def optimise(self, model: WaveModel, task: OptimisationTask):
        modifications = task.possible_modifications

        # TODO: run all combinations and find best

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, modifications)

        return OptimisationResults(simulation_result, modifications, [])


class DifferentialOptimisationStrategy(OptimisationStrategyAbstract):

    def obtain_numerical_chromosome(self, possible_modifications, mod_points_to_optimise):
        chromosome = []

        for modification in possible_modifications:
            points_to_encode = [[modification.points[i].x, modification.points[i].y] for i in
                                mod_points_to_optimise[modification.breaker_id]]
            chromosome.append(list(chain.from_iterable(points_to_encode)))
        return list(chain.from_iterable(chromosome))

    def build_breakers_from_genotype(self, genotype):
        # TODO
        return []

    def build_fitness(self, model, task, genotype):
        fitness_value = 0
        proposed_breakers = self.build_breakers_from_genotype(genotype)
        for obj in task.objectives:
            if obj is (CostObjective or NavigationObjective): #TODO expensive check can be missed? investigate
                fitness_value += obj.get_obj_value(model.domain, proposed_breakers)
            if obj is WaveObjective:
                #TODO read if already simulated
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers)
                fitness_value = obj.get_obj_value(model.domain, proposed_breakers, simulation_result)
        return fitness_value

    def optimise(self, model: WaveModel, task: OptimisationTask):
        # TODO implement deoptim

        # coords_bounds = [(0, model.domain.model_grid.spatial_step), (0, model.domain.model_grid.grid_x)]
        # optimisation_result=optimize.differential_evolution(fitness, )

        genotype = self.obtain_numerical_chromosome(task.possible_modifications, task.mod_points_to_optimise)
        print(genotype)
        evolutionary_modifications = []  # TODO fill

        best_modifications = []  # TODO best indiviual

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, best_modifications)

        return OptimisationResults(simulation_result, best_modifications, [])
