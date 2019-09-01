from scipy import optimize
from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Simulation.WaveModel import SwanWaveModel
import csv
import uuid
from functools import partial

from EvoAlgs.SPEA2.DefaultSPEA2 import DefaultSPEA2
from EvoAlgs.BreakersEvo.EvoOperators import calculate_objectives
from EvoAlgs.SPEA2.Operators import default_operators
from Optimisation.OptimisationStrategies.AbstractOptimisationStrategy import OptimisationStrategyAbstract, \
    OptimisationResults


class DifferentialOptimisationStrategy(OptimisationStrategyAbstract):

    def obtain_numerical_chromosome(self, task):
        chromosome = []
        for modification in task.possible_modifications:
            points_to_opt = task.mod_points_to_optimise[modification.breaker_id]
            points_to_encode = []
            prev_anchor = None
            for i in points_to_opt:
                anchor = modification.points[i + 1]
                prev_anchor = modification.points[i + 2]

                polar_coords = modification.points[i].point_to_relative_polar(anchor)

                # fill '-1' point to obtain next anchor
                modification.points[i].x = anchor.x + modification.points[i].x
                modification.points[i].y = anchor.y + modification.points[i].y

                real_angle = polar_coords["angle"]
                anchor_angle = anchor.point_to_relative_polar(prev_anchor)
                relative_angle = ((real_angle - anchor_angle) + 360 ) % 360
                points_to_encode.append([polar_coords["length"], relative_angle])

            chromosome.append(list(chain.from_iterable(points_to_encode)))
        return list(chain.from_iterable(chromosome))


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
                    print('BAD CONF')
                    return 9999
                # if model.expensive and (new_fitness/ base_fintess[obj_ind])  > sum(base_fintess):
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
                                                              popsize=20, maxiter=20, mutation=0.2, recombination=0.6,
                                                              seed=42, disp=True)

        best_genotype = optimisation_result.x
        print(np.round(best_genotype))

        best_modifications = self.build_breakers_from_genotype(best_genotype, task)

        simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers, best_modifications,
                                                                   ''.join(str(g) for g in best_genotype))

        return OptimisationResults(simulation_result, best_modifications, [])
