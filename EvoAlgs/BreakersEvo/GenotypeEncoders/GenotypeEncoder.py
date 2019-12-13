import copy
import random
from abc import abstractmethod

import numpy as np

from CommonUtils.StaticStorage import StaticStorage


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
    def onepoint_crossover(self, ancestor_genotype1, ancestor_genotype2):
        return

    @abstractmethod
    def space_fill(self):
        return


class DirectGenotypeEncoder(GenotypeEncoder):
    def _obtain_random_pair_indeces(self, chromosome_length, block_size, num_of_blocks):
        return random.sample(
            range(0, round(chromosome_length / block_size)), num_of_blocks)

    @abstractmethod
    def mutate_components(self, comp_values):
        return

    def mutate(self, ancestor_genotype):

        ancestor_genotype_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype, StaticStorage.task,
                                                                            StaticStorage.exp_domain.model_grid)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype_encoded)

        block_size = 2
        if any([g == 1 for g in self.genotype_mask]):
            num_of_blocks_to_mutate = round(len([ind for ind, g in enumerate(self.genotype_mask) if g == 0]) / 2)
        else:
            num_of_blocks_to_mutate = max(round(len(ancestor_genotype_encoded) / block_size / 4), 1)

        indexs_of_pairs_to_change = self._obtain_random_pair_indeces(len(ancestor_genotype_encoded), block_size,
                                                                     num_of_blocks_to_mutate)

        for block_id_index, block_id in enumerate(indexs_of_pairs_to_change):
            if self.genotype_mask[block_id * block_size] == 1:
                while self.genotype_mask[indexs_of_pairs_to_change[block_id_index] * block_size] == 1:
                    indexs_of_pairs_to_change[block_id_index] = self._obtain_random_pair_indeces(
                        len(ancestor_genotype_encoded),
                        block_size, 1)[0]

        for gen_ind in indexs_of_pairs_to_change:
            if self.genotype_mask[gen_ind * block_size] != 1:
                first_ind = gen_ind * block_size
                second_ind = gen_ind * block_size + 1
                new_encoded_genotype[first_ind], new_encoded_genotype[second_ind] = \
                    self.mutate_components((new_encoded_genotype[first_ind], new_encoded_genotype[second_ind]))

        old_chromosome_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype_encoded])
        new_chromosome_txt = ','.join([str(int(round(_))) for _ in new_encoded_genotype])

        print(f'Mutated:\n[{old_chromosome_txt}]\nto\n[{new_chromosome_txt}]')
        return self.parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                       StaticStorage.exp_domain.model_grid)

    def individual_crossover(self, ancestor_genotype1, ancestor_genotype2):

        ancestor_genotype1_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype1, StaticStorage.task,
                                                                             StaticStorage.exp_domain.model_grid)
        ancestor_genotype2_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype2, StaticStorage.task,
                                                                             StaticStorage.exp_domain.model_grid)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype1_encoded)

        block_size = 2

        if any([g == 1 for g in self.genotype_mask]):
            num_of_blocks_to_crossover = round(len([ind for ind, g in enumerate(self.genotype_mask) if g == 0]) / 2)
        else:
            num_of_blocks_to_crossover = max(round(len(ancestor_genotype1_encoded) / block_size / 4), 1)

        indexs_of_pairs_to_change = self._obtain_random_pair_indeces(len(ancestor_genotype1_encoded), block_size,
                                                                     num_of_blocks_to_crossover)

        for block_id_index, block_id in enumerate(indexs_of_pairs_to_change):
            if self.genotype_mask[block_id * block_size] == 1:
                while self.genotype_mask[indexs_of_pairs_to_change[block_id_index] * block_size] == 1:
                    indexs_of_pairs_to_change[block_id_index] = self._obtain_random_pair_indeces(
                        len(ancestor_genotype1_encoded),
                        block_size, 1)[0]

        for gen_ind in indexs_of_pairs_to_change:
            if self.genotype_mask[gen_ind * block_size] != 1 and self.genotype_mask[gen_ind * block_size + 1] != 1:
                first_ind = gen_ind * block_size
                second_ind = gen_ind * block_size + 1

                new_encoded_genotype[first_ind], new_encoded_genotype[second_ind] = self.crossover_components(
                    (ancestor_genotype1_encoded[first_ind], ancestor_genotype1_encoded[second_ind]),
                    (ancestor_genotype2_encoded[first_ind], ancestor_genotype2_encoded[second_ind]))

        old_chromosome1_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype1_encoded])
        old_chromosome2_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype2_encoded])
        new_chromosome_txt = ','.join([str(int(round(_))) for _ in new_encoded_genotype])

        print(
            f'Crossovered:\n[{old_chromosome1_txt}],\n[{old_chromosome2_txt}]\nto\n[{new_chromosome_txt}]')
        return self.parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                       StaticStorage.exp_domain.model_grid)

    def onepoint_crossover(self, ancestor_genotype1, ancestor_genotype2):
        ancestor_genotype1_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype1, StaticStorage.task,
                                                                             StaticStorage.exp_domain.model_grid)
        ancestor_genotype2_encoded = self.breakers_to_parameterized_genotype(ancestor_genotype2, StaticStorage.task,
                                                                             StaticStorage.exp_domain.model_grid)

        new_encoded_genotype = copy.deepcopy(ancestor_genotype1_encoded)

        block_size = 2
        num_of_split_points = 1

        indexs_of_pair_to_split = \
            self._obtain_random_pair_indeces(len(ancestor_genotype1_encoded) - block_size * 2, block_size,
                                             num_of_split_points)[0] + 1

        for gen_ind in range(0, round(len(new_encoded_genotype) / block_size)):
            if self.genotype_mask[gen_ind * block_size] != 1 and self.genotype_mask[gen_ind * block_size + 1] != 1:
                if gen_ind <= indexs_of_pair_to_split:
                    new_encoded_genotype[gen_ind * block_size] = ancestor_genotype1_encoded[gen_ind * block_size]
                    new_encoded_genotype[gen_ind * block_size + 1] = ancestor_genotype1_encoded[
                        gen_ind * block_size + 1]
                else:
                    new_encoded_genotype[gen_ind * block_size] = ancestor_genotype2_encoded[gen_ind * block_size]
                    new_encoded_genotype[gen_ind * block_size + 1] = ancestor_genotype2_encoded[
                        gen_ind * block_size + 1]

        old_chromosome1_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype1_encoded])
        old_chromosome2_txt = ','.join([str(int(round(_))) for _ in ancestor_genotype2_encoded])
        new_chromosome_txt = ','.join([str(int(round(_))) for _ in new_encoded_genotype])

        print(
            f'Crossovered by {indexs_of_pair_to_split}:\n[{old_chromosome1_txt}],\n[{old_chromosome2_txt}]\nto\n[{new_chromosome_txt}]')
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

        print(f'Initiated with encoding: [{new_chromosome_txt}]')
        return self.parameterized_genotype_to_breakers(new_encoded_genotype, StaticStorage.task,
                                                       StaticStorage.exp_domain.model_grid)
