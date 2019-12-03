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
    def breakers_to_parameterized_genotype(self, breakers, task, grid):
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
        self.genotype_mask = None


class AngularGenotypeEncoder:

    def __init__(self):
        self.min_for_init = [0, -75]
        self.max_for_init = [5, 75]
        self.pairwise = True
        self.genotype_mask = None

    def _obtain_random_pair_indeces(self, chromosome_length, block_size, num_of_blocks):
        return random.sample(
            range(0, round(chromosome_length / block_size)), num_of_blocks)

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
                    if modification.points[max(point_ids_to_optimise_in_modification)].x == -1:
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

    def mutate(self, ancestor_genotype):
        ancestor_genotype_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype, StaticStorage.task,
                                                                            StaticStorage.exp_domain.model_grid)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype_encoded)

        block_size = 2
        num_of_blocks_to_mutate = 1

        indexs_of_pairs_to_change = self._obtain_random_pair_indeces(len(ancestor_genotype_encoded), block_size,
                                                                     num_of_blocks_to_mutate)

        for block_id_index, block_id in enumerate(indexs_of_pairs_to_change):
            if self.genotype_mask[block_id * block_size] == 1:
                while self.genotype_mask[indexs_of_pairs_to_change[block_id_index] * block_size] == 1:
                    indexs_of_pairs_to_change[block_id_index] = self._obtain_random_pair_indeces(
                        len(ancestor_genotype_encoded),
                        block_size, 1)[0]

        mutation_ratio = abs(np.random.RandomState().normal(2, 1.5, 1)[0])
        mutation_ratio_dir = abs(np.random.RandomState().normal(35, 5, 1)[0])

        for gen_ind in indexs_of_pairs_to_change:
            if self.genotype_mask[gen_ind] != 1:
                sign = 1 if random.random() < 0.5 else -1

                len_ind = gen_ind * block_size
                dir_ind = gen_ind * block_size + 1
                new_encoded_genotype[len_ind] += sign * mutation_ratio
                new_encoded_genotype[len_ind] = abs(new_encoded_genotype[len_ind])
                new_encoded_genotype[dir_ind] += sign * mutation_ratio_dir
                new_encoded_genotype[dir_ind] = max(new_encoded_genotype[dir_ind], self.min_for_init[1])
                new_encoded_genotype[dir_ind] = min(new_encoded_genotype[dir_ind], self.max_for_init[1])

        old_chromosome_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype_encoded])
        new_chromosome_txt = ','.join([str(int(round(_))) for _ in new_encoded_genotype])

        print(f'Mutated with angular encoding:\n[{old_chromosome_txt}]\nto\n[{new_chromosome_txt}]')
        return self.parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                       StaticStorage.exp_domain.model_grid)

    def crossover(self, ancestor_genotype1, ancestor_genotype2):

        ancestor_genotype1_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype1, StaticStorage.task,
                                                                             StaticStorage.exp_domain.model_grid)
        ancestor_genotype2_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype2, StaticStorage.task,
                                                                             StaticStorage.exp_domain.model_grid)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype1_encoded)

        block_size = 2
        num_of_blocks_to_crossover = 1

        indexs_of_pairs_to_change = self._obtain_random_pair_indeces(len(ancestor_genotype1_encoded), block_size,
                                                                     num_of_blocks_to_crossover)

        for block_id_index, block_id in enumerate(indexs_of_pairs_to_change):
            if self.genotype_mask[block_id * block_size] == 1:
                while self.genotype_mask[indexs_of_pairs_to_change[block_id_index] * block_size] == 1:
                    indexs_of_pairs_to_change[block_id_index] = self._obtain_random_pair_indeces(
                        len(ancestor_genotype1_encoded),
                        block_size, 1)[0]

        angle_parent_id = random.randint(0, 1)

        part1_rate = abs(random.random())
        part2_rate = 1 - part1_rate

        for gen_ind in indexs_of_pairs_to_change:
            if self.genotype_mask[gen_ind * block_size] != 1 and self.genotype_mask[gen_ind * block_size + 1] != 1:
                len_ind = gen_ind * block_size
                dir_ind = gen_ind * block_size + 1
                new_encoded_genotype[len_ind] = round(ancestor_genotype1_encoded[len_ind] * part1_rate +
                                                      ancestor_genotype2_encoded[len_ind] * part2_rate)

                if angle_parent_id == 0:
                    new_encoded_genotype[dir_ind] = round((ancestor_genotype1_encoded[dir_ind] + 360) % 360)
                if angle_parent_id == 1:
                    new_encoded_genotype[dir_ind] = round((ancestor_genotype2_encoded[dir_ind] + 360) % 360)

        old_chromosome1_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype1_encoded])
        old_chromosome2_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype2_encoded])
        new_chromosome_txt = ','.join([str(int(round(_))) for _ in new_encoded_genotype])

        print(
            f'Crossovered with angular encoding:\n[{old_chromosome1_txt}],\n[{old_chromosome2_txt}]\nto\n[{new_chromosome_txt}]')
        return self.parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                       StaticStorage.exp_domain.model_grid)

    def space_fill(self, reference_genotype):
        base_genotype_encoded = self.breakers_to_parameterized_genotype(reference_genotype, StaticStorage.task,
                                                                        StaticStorage.exp_domain.model_grid)

        new_encoded_genotype = copy.deepcopy(base_genotype_encoded)

        self.genotype_mask = np.zeros(len(new_encoded_genotype))

        for j, g in enumerate(new_encoded_genotype):
            if j % 2 == 0:
                new_encoded_genotype[j] = random.randint(self.min_for_init[0],
                                                         self.max_for_init[0])
            else:
                new_encoded_genotype[j] = random.randint(self.min_for_init[1],
                                                         self.max_for_init[1])

        new_chromosome_txt = ','.join([str(int(round(_))) for _ in new_encoded_genotype])

        print(f'Initiated with angular encoding: [{new_chromosome_txt}]')
        return self.parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                       StaticStorage.exp_domain.model_grid)
