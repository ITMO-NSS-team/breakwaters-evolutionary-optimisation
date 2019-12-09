import random
import copy
import numpy as np

from EvoAlgs.BreakersEvo.GenotypeEncoders.GenotypeEncoder import DirectGenotypeEncoder


class CartesianGenotypeEncoder(DirectGenotypeEncoder):

    def __init__(self):
        self.min_for_init = [-4, -4]
        self.max_for_init = [4, 4]

    def parameterized_genotype_to_breakers(self, genotype, task, grid):
        gen_id = 0
        new_modifications = []

        for modification in task.possible_modifications:
            converted_modification = copy.deepcopy(modification)
            if converted_modification.breaker_id in task.mod_points_to_optimise:
                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[converted_modification.breaker_id]

                anchor_point = converted_modification.points[max(point_ids_to_optimise_in_modification) + 1]

                for point_ind in point_ids_to_optimise_in_modification:
                    converted_modification.points[point_ind].x = genotype[gen_id] + anchor_point.x
                    converted_modification.points[point_ind].y = genotype[gen_id + 1] + anchor_point.y
                    gen_id += 2

            new_modifications.append(converted_modification)

        assert new_modifications is not None
        return new_modifications

    def breakers_to_parameterized_genotype(self, breakers, task, grid):
        chromosome = []

        for modification in task.possible_modifications:
            converted_modification = copy.deepcopy(modification)
            if converted_modification.breaker_id in task.mod_points_to_optimise:

                breaker = [b for b in breakers if b.breaker_id == converted_modification.breaker_id][0]

                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[converted_modification.breaker_id]

                anchor_point = converted_modification.points[max(point_ids_to_optimise_in_modification) + 1]

                for point_ind in point_ids_to_optimise_in_modification:
                    if breaker.points[max(point_ids_to_optimise_in_modification)].x == -1:
                        x = 0
                        y = 0
                        anchor_point = converted_modification.points[point_ind]
                    else:
                        last_point = breaker.points[max(point_ids_to_optimise_in_modification)]
                        x = last_point.x - anchor_point.x
                        y = last_point.y - anchor_point.y

                        anchor_point = last_point
                    chromosome.append(x)
                    chromosome.append(y)

        assert chromosome is not None

        return chromosome

    def mutate_components(self, comp_values):
        mutation_params = [2, 0.5, 1]
        mutation_ratio_x = abs(
            np.random.RandomState().normal(mutation_params[0], mutation_params[1],
                                           mutation_params[2])[0])

        mutation_ratio_y = abs(
            np.random.RandomState().normal(mutation_params[0], mutation_params[1],
                                           mutation_params[2])[0])

        sign = 1 if random.random() < 0.5 else -1

        comp_value1 = comp_values[0]
        comp_value1 += sign * mutation_ratio_x
        comp_value1 = round(abs(comp_value1))

        comp_value2 = comp_values[1]
        comp_value2 += sign * mutation_ratio_y
        comp_value2 = round(abs(comp_value2))

        return comp_value1, comp_value2

    def crossover_components(self, comp_values1, comp_values2):
        part1_rate = abs(random.random())
        part2_rate = 1 - part1_rate

        new_value1 = round(comp_values1[0] * part1_rate +
                           comp_values2[0] * part2_rate)

        part1_rate = abs(random.random())
        part2_rate = 1 - part1_rate

        new_value2 = round(comp_values1[0] * part1_rate +
                           comp_values2[0] * part2_rate)

        return new_value1, new_value2

    def mutate(self, ancestor_genotype):
        return super(CartesianGenotypeEncoder, self).mutate(ancestor_genotype)

    def crossover(self, ancestor_genotype1, ancestor_genotype2):
        return super(CartesianGenotypeEncoder, self).crossover(ancestor_genotype1, ancestor_genotype2,
                                                               self.crossover_components)
