import copy
import random
from math import sqrt
from operator import itemgetter

from EvoAlgs.SPEA2.RawFitness import raw_fitness


class SPEA2:
    def __init__(self, params, calculate_objectives, evolutionary_operators):
        '''
         Strength Pareto Evolutionary Algorithm
        :param params: Meta-parameters of the SPEA2
        :param calculate_objectives: function to calculate objective functions for each individual in population
        :param evolutionary_operators: EvoOperators class that encapsulates all evolutionary operators
        '''

        self.params = params

        self.calculate_objectives = calculate_objectives
        self.operators = evolutionary_operators

        self.__init_operators()
        self.__init_populations()

        self.genotype_mask = None

    def __init_operators(self):
        self.init_population = self.operators.init_population
        self.crossover = self.operators.crossover
        self.mutation = self.operators.mutation

    def __init_populations(self):
        gens = self.init_population(self.params.pop_size)
        self._pop = [SPEA2.Individ(genotype=gen) for gen in gens]
        self._archive = []

    class Params:
        def __init__(self, max_gens, pop_size, archive_size, crossover_rate, mutation_rate, mutation_value_rate):
            self.max_gens = max_gens
            self.pop_size = pop_size

            self.archive_size = archive_size

            self.crossover_rate = crossover_rate
            self.mutation_rate = mutation_rate
            self.mutation_value_rate = mutation_value_rate

            # TODO: these params should not be here
            self.initial_fid_time = 180
            self.initial_fid_spatial = 56

            self.fid_time_delta = 0
            self.fid_spatial_delta = 0

            self.refinement_radius = 0
            self.refinement_radius_delta = 0

    class Individ:
        def __init__(self, genotype):
            self.objectives = ()
            self.genotype = genotype
            self.dominators = []
            self.raw_fitness = 0
            self.density = 0
            self.referenced_dataset = None

        def fitness(self):
            return self.raw_fitness + self.density

        # def weighted_sum(self):
        # return sum(list(self.calculate_objectives))

    class ErrorHistory:
        class Point:
            def __init__(self, genotype="", genotype_index=0, fitness_value=pow(10, 9), error_value=pow(10, 9)):
                self.genotype = genotype
                self.genotype_index = genotype_index
                self.fitness_value = fitness_value
                self.error_value = error_value

        def __init__(self):
            self.history = []

        def add_new(self, genotype, genotype_index, fitness, error):
            self.history.append(
                SPEA2.ErrorHistory.Point(genotype=copy.deepcopy(genotype), genotype_index=genotype_index,
                                         fitness_value=fitness, error_value=error))

        def last(self):
            return SPEA2.ErrorHistory.Point() if len(self.history) == 0 else self.history[-1]

    def solution(self, verbose=True, **kwargs):
        pass

    def fitness(self):
        self.calculate_objectives(self._pop)
        union = self._archive + self._pop

        raw_values = raw_fitness(union)
        for idx in range(len(union)):
            union[idx].raw_fitness = raw_values[idx]

        for p in union:
            p.density = self.calculate_density(p, union)

    def calculate_density(self, src, pop):
        '''
        Estimate the density of Pareto front given k-nearest neighbour of src
        :param src:
        :param pop:
        :return:
        '''
        distances_to_src = []
        for p in pop:
            distances_to_src.append(self.euclidean_distance(src.objectives, p.objectives))
        distances_to_src = sorted(distances_to_src)

        k = int(sqrt(self.params.pop_size + self.params.archive_size))

        density = 1.0 / (distances_to_src[k] + 2.0)
        return density

    def euclidean_distance(self, p1, p2):
        sum = 0
        for idx in range(len(p1)):
            sum += pow(p1[idx] - p2[idx], 2)

        return sqrt(sum)

    def environmental_selection(self, pop, archive):
        union = archive + pop
        env = [p for p in union if p.fitness() < 1.0]

        if len(env) < self.params.archive_size:
            # Fill the archive with the remaining candidate solutions
            union.sort(key=lambda p: p.fitness())
            for p in union:
                if len(env) >= self.params.archive_size:
                    break
                if p.fitness() >= 1.0:
                    env.append(p)
        elif len(env) > self.params.archive_size:
            while True:
                # Truncate the archive population
                k = int(sqrt(len(env)))
                dens = []
                for p1 in env:
                    distances_to_p1 = []
                    for p2 in env:
                        distances_to_p1.append(self.euclidean_distance(p1.objectives, p2.objectives))
                    distances_to_p1 = sorted(distances_to_p1)
                    density = 1.0 / (distances_to_p1[k] + 2.0)
                    dens.append((p1, density))
                dens.sort(key=itemgetter(1))
                to_remove = dens[0][0]
                env.remove(to_remove)

                if len(env) <= self.params.archive_size:
                    break
        return env

    def selected(self, size, pop):
        selected = []
        while len(selected) < size:
            selected.append(self.binary_tournament(pop))

        return selected

    def binary_tournament(self, pop):

        i, j = random.randint(0, len(pop) - 1), random.randint(0, len(pop) - 1)

        while j == i:
            j = random.randint(0, len(pop) - 1)
        return pop[i] if pop[i].fitness() < pop[j].fitness() else pop[j]

    def reproduce(self, selected, pop_size):
        children = []

        for p1 in selected:
            idx = selected.index(p1)
            if idx + 1 > len(selected) - 1:
                idx = len(selected) - 1 - 1
            if idx == 0: idx = 1
            p2 = selected[idx + 1] if idx % 2 == 0 else selected[idx - 1]
            if idx == len(selected) - 1:
                p2 = selected[0]

            child_gen = self.crossover(p1.genotype, p2.genotype, self.params.crossover_rate, self.genotype_mask)
            child_gen = self.mutation(child_gen, self.params.mutation_rate, self.params.mutation_value_rate,
                                      self.genotype_mask)
            child = SPEA2.Individ(genotype=child_gen)
            children.append(child)

            if len(children) >= pop_size:
                break

        return children
