from abc import abstractmethod
import random


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


class DirectGenotypeEncoder(GenotypeEncoder):
    def _obtain_random_pair_indeces(self, chromosome_length, block_size, num_of_blocks):
        return random.sample(
            range(0, round(chromosome_length / block_size)), num_of_blocks)
