from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Simulation.WaveModel import SwanWaveModel
import csv
import uuid


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
            points_to_opt = task.mod_points_to_optimise[modification.breaker_id]
            points_to_encode = []
            for i in points_to_opt:
                anchor = modification.points[i + 1]
                polar_coords = modification.points[i].point_to_relative_polar(anchor)

                # fill '-1' point for next anchor
                modification.points[i].x = anchor.x + modification.points[i].x
                modification.points[i].y = anchor.y + modification.points[i].y

                points_to_encode.append([polar_coords["length"], polar_coords["angle"]])

            chromosome.append(list(chain.from_iterable(points_to_encode)))
        return list(chain.from_iterable(chromosome))

    def build_breakers_from_genotype(self, genotype, task):
        gen_id = 0

        new_modifications = []

        for modification in task.possible_modifications:

            point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

            anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]

            for point_ind in point_ids_to_optimise_in_modification:
                modification.points[point_ind] = modification.points[point_ind].from_polar(genotype[gen_id],
                                                                                           genotype[gen_id + 1],
                                                                                           anchor_point)
                gen_id += 2
                anchor_point = modification.points[point_ind]
            new_modifications.append(modification)
        return new_modifications

    def calculate_fitness(self, genotype, model, task, base_fintess):
        fitness_value = 0
        # print(genotype)

        genotype = [int(round(g, 0)) for g in genotype]
        # print(f'geno_{genotype}')

        proposed_breakers = self.build_breakers_from_genotype(genotype, task)

        obj_ind = 0
        for obj_ind, obj in enumerate(task.objectives):
            if isinstance(obj, (CostObjective, NavigationObjective, StructuralObjective)):
                # TODO expensive check can be missed? investigate
                new_fitness = obj.get_obj_value(model.domain, proposed_breakers)
                if new_fitness is None:
                    print ('BAD CONF')
                    return 9999
                #if model.expensive and (new_fitness/ base_fintess[obj_ind])  > sum(base_fintess):
                #   print ('TOO EXP')
                #   return 9999
                fitness_value += (new_fitness / base_fintess[obj_ind]) * obj.importance
            if isinstance(obj, WaveHeightObjective):
                # TODO read if already simulated
                # configuration_label = ''.join(str(g) for g in genotype)

                txt = []
                for pb in proposed_breakers:
                    for pbp in pb.points:
                        txt.append(str(int(pbp.x)))
                        txt.append(str(int(pbp.y)))
                txt_genotype = ",".join(txt)

                config_exists = False
                configuration_label = uuid.uuid4().hex

                if model.expensive:
                    with open('D://Projects//Sochi-prichal//breakwater-evo-opt//configs_catalog.csv',
                              mode='r', newline='') as csv_file:
                        sim_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
                        for row in sim_reader:
                            if row[1] == txt_genotype:
                                configuration_label = row[0]
                                config_exists = True
                                break
                    if not config_exists:
                        with open('D://Projects//Sochi-prichal//breakwater-evo-opt//configs_catalog.csv',
                                  mode='a', newline='') as csv_file:
                            sim_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                            sim_writer.writerow([f'{configuration_label}', txt_genotype])

                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers, configuration_label)
                fitness_value += \
                    (obj.get_obj_value(model.domain, proposed_breakers, simulation_result) \
                     / base_fintess[obj_ind]) * obj.importance
            obj_ind += 1

        return fitness_value / len(task.objectives)

    def calculate_default_fitness(self, genotype, model, task):
        fitness_value = []

        genotype = [int(round(g, 0)) for g in genotype]

        proposed_breakers = self.build_breakers_from_genotype(genotype, task)
        for obj in task.objectives:
            if isinstance(obj, (CostObjective, NavigationObjective, StructuralObjective)):
                # TODO expensive check can be missed? investigate
                new_fitness = obj.get_obj_value(model.domain, proposed_breakers)
                if new_fitness is None:
                    new_fitness = 9999
                fitness_value.append(new_fitness)
            if isinstance(obj, WaveHeightObjective):
                # TODO read if already simulated

                # configuration_label = ''.join(str(g) for g in genotype)

                txt = []
                for pb in proposed_breakers:
                    for pbp in pb.points:
                        txt.append(str(int(pbp.x)))
                        txt.append(str(int(pbp.y)))
                txt_genotype = ",".join(txt)

                config_exists = False
                configuration_label = uuid.uuid4().hex

                if isinstance(model, SwanWaveModel):
                    with open('D://Projects//Sochi-prichal//breakwater-evo-opt//configs_catalog.csv',
                              mode='r', newline='') as csv_file:
                        sim_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
                        for row in sim_reader:
                            if row[1] == txt_genotype:
                                configuration_label = row[0]
                                config_exists = True
                                break
                    if not config_exists:
                        with open('D://Projects//Sochi-prichal//breakwater-evo-opt//configs_catalog.csv',
                                  mode='a', newline='') as csv_file:
                            sim_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                            sim_writer.writerow([f'{configuration_label}', txt_genotype])

                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers, configuration_label)
                fitness_value.append(obj.get_obj_value(model.domain, proposed_breakers, simulation_result))

        return fitness_value

    def optimise(self, model: WaveModel, task: OptimisationTask):
        genotype = self.obtain_numerical_chromosome(task)

        coords_bounds = [(0, 359) if x % 2 else (0, 6) for x in range(0, len(genotype))]

        default_fitness = self.calculate_default_fitness([0] * len(genotype), model, task)

        print('def fitness {}'.format(default_fitness))

        optimisation_result = optimize.differential_evolution(self.calculate_fitness, coords_bounds,
                                                              args=(model, task, default_fitness),
                                                              popsize=40, maxiter=80, mutation=0.2, recombination=0.6,
                                                              seed=42, disp=True)

        best_genotype = optimisation_result.x
        print(np.round(best_genotype))

        best_modifications = self.build_breakers_from_genotype(best_genotype, task)

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, best_modifications,
                                                                   ''.join(str(g) for g in best_genotype))

        return OptimisationResults(simulation_result, best_modifications, [])
