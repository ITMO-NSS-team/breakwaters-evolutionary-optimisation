from abc import abstractmethod
import copy
import random
from CommonUtils.StaticStorage import StaticStorage
import numpy as np


class GenotypeEncoder:
    @abstractmethod
    def parameterized_genotype_to_breakers(self, genotype, task, grid):
        return

    @abstractmethod
    def breakers_to_parameterized_genotype(self, breakers):
        return

    @abstractmethod
    def mutate(self, ancestor_genotype):
        return

    @abstractmethod
    def crossover(self, ancestor_genotype1, ancestor_genotype2):
        return

    @abstractmethod
    def space_fill(self):
        return


class CartesianGenotypeEncoder:

    def __init__(self):
        self.min_for_init = [-3, -3]
        self.max_for_init = [3, 3]
        self.pairwise = True

    def parameterized_genotype_to_breakers(self, genotype, task, grid):
        gen_id = 0
        new_modifications = []

        for modification in task.possible_modifications:

            if modification.breaker_id in task.mod_points_to_optimise:
                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

                anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]
                prev_anchor = modification.points[max(point_ids_to_optimise_in_modification) + 2]

                for point_ind in point_ids_to_optimise_in_modification:
                    anchor_angle = anchor_point.get_relative_polar_coordinates(prev_anchor)["angle"]

                    length = genotype[gen_id]
                    direction = (genotype[gen_id + 1] + anchor_angle + 360) % 360

                    modification.points[point_ind] = modification.points[point_ind].from_polar(length,
                                                                                               direction,
                                                                                               anchor_point, grid)
                    gen_id += 2
                    prev_anchor = anchor_point
                    anchor_point = modification.points[point_ind]
                new_modifications.append(modification)
        return new_modifications

    def breakers_to_parameterized_genotype(breakers):
        txt = []
        for pb in breakers:
            for pbp in pb.points:
                txt.append(str(int(pbp.x)))
                txt.append(str(int(pbp.y)))
        txt_genotype = ",".join(txt)
        return txt_genotype


class AngularGenotypeEncoder:

    def __init__(self):
        self.min_for_init = [0, -50]
        self.max_for_init = [5, 50]
        self.pairwise = True

    def parameterized_genotype_to_breakers(self, genotype, task, grid):
        gen_id = 0
        new_modifications = []

        for modification in task.possible_modifications:

            if modification.breaker_id in task.mod_points_to_optimise:
                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

                anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]
                prev_anchor = modification.points[max(point_ids_to_optimise_in_modification) + 2]

                for point_ind in point_ids_to_optimise_in_modification:
                    anchor_angle = anchor_point.get_relative_polar_coordinates(prev_anchor)["angle"]

                    length = genotype[gen_id]
                    direction = (genotype[gen_id + 1] + anchor_angle + 360) % 360

                    modification.points[point_ind] = modification.points[point_ind].from_polar(length,
                                                                                               direction,
                                                                                               anchor_point, grid)
                    gen_id += 2
                    prev_anchor = anchor_point
                    anchor_point = modification.points[point_ind]
                new_modifications.append(modification)
        return new_modifications

    def breakers_to_parameterized_genotype(self,breakers,task, grid):
        gen_id = 0
        chromosome = []

        for modification in task.possible_modifications:

            if modification.breaker_id in task.mod_points_to_optimise:
                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

                anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]
                prev_anchor = modification.points[max(point_ids_to_optimise_in_modification) + 2]

                for point_ind in point_ids_to_optimise_in_modification:
                    anchor_angle = anchor_point.get_relative_polar_coordinates(prev_anchor)["angle"]

                    length = 2
                    direction = anchor_angle
                    #direction = (genotype[gen_id + 1] + anchor_angle + 360) % 360

                    #modification.points[point_ind] = modification.points[point_ind].from_polar(length,
                    #                                                                           direction,
                    #                                                                           anchor_point, grid)
                    prev_anchor = anchor_point
                    anchor_point = modification.points[point_ind]
                chromosome.append(length)
                chromosome.append(direction)
        return chromosome

    @abstractmethod
    def mutate(self, ancestor_genotype):
        ancestor_genotype_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype_encoded)

        block_size = 2
        num_of_blocks_to_crossover = 1

        indexs_of_pairs_to_change = random.sample(
            range(0, round(len(ancestor_genotype_encoded) / block_size), num_of_blocks_to_crossover))

        mutation_ratio = abs(np.random.RandomState().normal(2, 1.5, 1)[0])
        mutation_ratio_dir = abs(np.random.RandomState().normal(15, 5, 1)[0])

        part1_rate = abs(random.random())
        part2_rate = 1 - part1_rate

        genotype_mask = None

        for gen_ind in indexs_of_pairs_to_change:
            if genotype_mask is None or gen_ind not in genotype_mask:
                sign = 1 if random.random() < 0.5 else -1

                len_ind = gen_ind * block_size
                dir_ind = gen_ind * block_size + 1
                new_encoded_genotype[len_ind] += sign * mutation_ratio
                new_encoded_genotype[len_ind] = abs(new_encoded_genotype[len_ind])
                new_encoded_genotype[dir_ind] += sign * mutation_ratio_dir
                new_encoded_genotype[dir_ind] = max(new_encoded_genotype[dir_ind], self.min_for_init[1])
                new_encoded_genotype[dir_ind] = min(new_encoded_genotype[dir_ind], self.min_for_init[1])
            else:
                next()

        return self._parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                        StaticStorage.model.grid)

    @abstractmethod
    def crossover(self, ancestor_genotype1, ancestor_genotype2):

        ancestor_genotype1_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype1)
        ancestor_genotype2_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype2)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype1_encoded)

        block_size = 2
        num_of_blocks_to_crossover = 1

        indexs_of_pairs_to_change = random.sample(
            range(0, round(len(ancestor_genotype1_encoded) / block_size), num_of_blocks_to_crossover))

        angle_parent_id = random.randint(0, 1)

        part1_rate = abs(random.random())
        part2_rate = 1 - part1_rate

        genotype_mask = None

        for gen_ind in indexs_of_pairs_to_change:
            if genotype_mask is None or gen_ind not in genotype_mask:
                len_ind = gen_ind * block_size
                dir_ind = gen_ind * block_size + 1
                new_encoded_genotype[len_ind] = round(ancestor_genotype1_encoded[len_ind] * part1_rate +
                                                      ancestor_genotype2_encoded[len_ind] * part2_rate)
            else:
                next()

        if angle_parent_id == 0:
            new_encoded_genotype[dir_ind] = round((ancestor_genotype1_encoded.genotype_array[dir_ind] + 360) % 360)
        if angle_parent_id == 1:
            new_encoded_genotype[dir_ind] = round((ancestor_genotype2_encoded.genotype_array[dir_ind] + 360) % 360)

        return self._parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                        StaticStorage.model.grid)

    @abstractmethod
    def space_fill(self):
        return
