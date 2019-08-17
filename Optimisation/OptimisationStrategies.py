from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *

from Simulation import WaveModel


class OptimisationResults(object):
    def __init__(self, simulation_result, modifications, history):
        self.simulation_result = simulation_result
        self.modifications = modifications
        self.history = history


class OptimisationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def optimise(self, model: WaveModel, task: OptimisationTask) -> OptimisationResults:
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

    def obtain_numerical_chromosome(self, task):
        chromosome = []

        for modification in task.possible_modifications:
            points_to_encode = [[modification.points[i].x, modification.points[i].y] for i in
                                task.mod_points_to_optimise[modification.breaker_id]]
            chromosome.append(list(chain.from_iterable(points_to_encode)))
        return list(chain.from_iterable(chromosome))

    def build_breakers_from_genotype(self, genotype, task):
        gen_id = 0

        new_modifications = []

        for modification in task.possible_modifications:

            point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

            if max(point_ids_to_optimise_in_modification) + 1 != len(modification.points):
                # anchor for the calculation of relative displacement of optimised breakwater segments
                anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]
            else:
                # works only for opt point in the beginning of breakwater
                raise NotImplementedError

            for point_ind in point_ids_to_optimise_in_modification:
                modification.points[point_ind].x = np.round(genotype[gen_id], 0) + anchor_point.x
                gen_id += 1
                modification.points[point_ind].y = np.round(genotype[gen_id], 0) + anchor_point.y
                gen_id += 1
            new_modifications.append(modification)
        return new_modifications

    def calculate_fitness(self, genotype, model, task, base_fintess):
        fitness_value = 0
        # print(genotype)

        proposed_breakers = self.build_breakers_from_genotype(genotype, task)
        obj_ind = 0
        for obj in task.objectives:
            if isinstance(obj, CostObjective) or isinstance(obj, NavigationObjective):
                # TODO expensive check can be missed? investigate
                fitness_value += obj.get_obj_value(model.domain, proposed_breakers) / base_fintess[obj_ind]
            if isinstance(obj, WaveHeightObjective):
                # TODO read if already simulated
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers)
                fitness_value += (obj.get_obj_value(model.domain, proposed_breakers, simulation_result)) / base_fintess[
                    obj_ind]
            obj_ind += 1
        return fitness_value / 3

    def calculate_default_fitness(self, genotype, model, task):
        fitness_value = []
        # print(genotype)
        proposed_breakers = self.build_breakers_from_genotype(genotype, task)
        for obj in task.objectives:
            if isinstance(obj, CostObjective) or isinstance(obj, NavigationObjective):
                # TODO expensive check can be missed? investigate
                fitness_value.append(obj.get_obj_value(model.domain, proposed_breakers))
            if isinstance(obj, WaveHeightObjective):
                # TODO read if already simulated
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers)
                fitness_value.append(obj.get_obj_value(model.domain, proposed_breakers, simulation_result))
        return fitness_value

    def optimise(self, model: WaveModel, task: OptimisationTask):
        # TODO implement deoptim
        genotype = self.obtain_numerical_chromosome(task)

        coords_bounds = list((-5, 5) for _ in range(len(genotype)))

        def_fitness = self.calculate_default_fitness([0] * len(genotype), model, task)

        print('def fitness {}'.format(def_fitness))

        optimisation_result = optimize.differential_evolution(self.calculate_fitness, coords_bounds,
                                                              args=(model, task, def_fitness),
                                                              popsize=40, maxiter=40, mutation=0.5, recombination=0.5,
                                                              seed=42, disp=True)

        best_genotype = optimisation_result.x
        print(np.round(best_genotype))

        best_modifications = self.build_breakers_from_genotype(best_genotype, task)

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, best_modifications)

        return OptimisationResults(simulation_result, best_modifications, [])
