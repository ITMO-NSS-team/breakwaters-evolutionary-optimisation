import copy
import random
import numpy as np
from EvoAlgs.BreakersEvo.GenotypeEncoders.GenotypeEncoder import DirectGenotypeEncoder


class AngularGenotypeEncoder(DirectGenotypeEncoder):

    def __init__(self):
        self.min_for_init = [0, -75]
        self.max_for_init = [5, 75]

    def parameterized_genotype_to_breakers(self, genotype, task, grid):
        gen_id = 0
        new_modifications = []

        for modification in task.possible_modifications:
            converted_modification = copy.deepcopy(modification)

            if converted_modification.breaker_id in task.mod_points_to_optimise:
                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[converted_modification.breaker_id]

                anchor_point = converted_modification.points[max(point_ids_to_optimise_in_modification) + 1]
                prev_anchor = converted_modification.points[max(point_ids_to_optimise_in_modification) + 2]

                for point_ind in point_ids_to_optimise_in_modification:
                    anchor_angle = anchor_point.get_relative_polar_coordinates(prev_anchor)["angle"]

                    length = genotype[gen_id]
                    direction = (genotype[gen_id + 1] + anchor_angle + 360) % 360

                    converted_modification.points[point_ind] = converted_modification.points[point_ind].from_polar(
                        length,
                        direction,
                        anchor_point, grid)
                    gen_id += 2
                    prev_anchor = anchor_point
                    anchor_point = converted_modification.points[point_ind]
                new_modifications.append(converted_modification)
        return new_modifications

    def breakers_to_parameterized_genotype(self, breakers, task, grid):
        chromosome = []

        for modification in task.possible_modifications:

            if modification.breaker_id in task.mod_points_to_optimise:

                breaker = [b for b in breakers if b.breaker_id == modification.breaker_id][0]

                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

                anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]
                prev_anchor = modification.points[max(point_ids_to_optimise_in_modification) + 2]

                for point_ind in point_ids_to_optimise_in_modification:
                    anchor_angle = anchor_point.get_relative_polar_coordinates(prev_anchor)["angle"]
                    if breaker.points[max(point_ids_to_optimise_in_modification)].x == -1:
                        length = 0
                        direction = anchor_angle
                        prev_anchor = anchor_point
                        anchor_point = modification.points[point_ind]
                    else:
                        last_point = breaker.points[max(point_ids_to_optimise_in_modification)]

                        length = last_point.get_relative_polar_coordinates(anchor_point)["length"]
                        direction = last_point.get_relative_polar_coordinates(anchor_point)["angle"]

                        prev_anchor = anchor_point
                        anchor_point = last_point
                    chromosome.append(length)
                    chromosome.append(direction)
        return chromosome

    def mutate_components(self, comp_values):
        mutation_params_len = [2, 1.5, 1]
        mutation_params_dir = [35, 5, 1]

        mutation_ratio_len = abs(
            np.random.normal(mutation_params_len[0], mutation_params_len[1],
                             mutation_params_len[2])[0])

        mutation_ratio_dir = abs(
            np.random.normal(mutation_params_dir[0], mutation_params_dir[1],
                             mutation_params_dir[2])[0])

        sign = 1 if random.random() < 0.5 else -1

        comp_value1 = comp_values[0]
        comp_value1 += sign * mutation_ratio_len
        comp_value1 = round(abs(comp_value1))

        comp_value2 = comp_values[1]
        comp_value2 += sign * mutation_ratio_dir
        comp_value2 = max(comp_value2, self.min_for_init[1])
        comp_value2 = min(comp_value2, self.max_for_init[1])

        return comp_value1, comp_value2

    def crossover_components(self, comp_values1, comp_values2):
        part1_rate = abs(random.random())
        part2_rate = 1 - part1_rate

        new_value1 = round(comp_values1[0] * part1_rate +
                           comp_values2[0] * part2_rate)

        rate = abs(random.random())

        if rate < 0.5:
            new_value2 = comp_values1[1]
        else:
            new_value2 = comp_values2[1]

        return new_value1, new_value2

    def mutate(self, ancestor_genotype):
        return super(AngularGenotypeEncoder, self).mutate(ancestor_genotype)

    def crossover(self, ancestor_genotype1, ancestor_genotype2):
        raise NotImplementedError
