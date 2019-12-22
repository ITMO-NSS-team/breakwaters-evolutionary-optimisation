import copy
import random
from math import sqrt
from operator import itemgetter
import numpy as np
from random import randint, random

from EvoAlgs.SPEA2.RawFitness import raw_fitness
from CommonUtils.StaticStorage import StaticStorage


class DE_:
    def __init__(self, params, calculate_objectives, evolutionary_operators, visualiser, greedy_heuristic):
        '''
         Differential Evolution Algorithm (DE)
        '''

        self.params = params

        self.calculate_objectives = calculate_objectives
        self.operators = evolutionary_operators

        self.__init_operators()
        self.__init_populations()

        self.visualiser = visualiser
        self.greedy_heuristic = greedy_heuristic

    def __init_operators(self):
        self.init_population = self.operators.init_population
        self.crossover = self.operators.crossover
        self.mutation = self.operators.mutation

    def __init_populations(self):

        gens = self.init_population(self.params.pop_size)
        self._pop = [DE_.Individ(genotype=gen) for gen in gens]
        self.clone = None

    class Params:
        def __init__(self, max_gens, pop_size, crossover_rate, mutation_rate, mutation_value_rate,
                     min_or_max):
            self.max_gens = max_gens
            self.pop_size = pop_size
            self.goal = min_or_max
            self.crossover_rate = crossover_rate
            self.mutation_rate = mutation_rate
            self.mutation_value_rate = mutation_value_rate

    class Individ:
        def __init__(self, genotype):
            self.objectives = ()
            self.analytics_objectives = []
            self.fitness = None
            self.genotype = copy.deepcopy(genotype)
            self.dominators = []
            self.raw_fitness = 0
            self.density = 0
            self.population_number = 0
            self.referenced_dataset = None

    def solution(self, verbose=True, **kwargs):
        pass

    def fitness(self):

        self.calculate_objectives(population=self._pop, visualiser=self.visualiser)
        self.clone = copy.deepcopy(
            self._pop[np.argmin([ind.objectives[0] for ind in self._pop])])  # the best individual from population

    def proportional_selection(
            self):  # need to modify fitness function value (normalize it to 0-1 range) to use this type of selection
        fitnesses_sum = sum([ind.objectives[0] for ind in self._pop])

        selected_indexes = []
        for j in range(len(self._pop) * 2):
            randomnum = randint(0, 10000)
            randomnum = randomnum / 10000.0
            check = 0
            for i in range(len(self._pop)):
                check += (self._pop[i].objectives[0] / fitnesses_sum)
                if check >= randomnum:
                    selected_indexes.append(self._pop[i])
                    break
                elif i == len(self._pop) - 1:
                    selected_indexes.append(self._pop[i])

        return selected_indexes

    def rank_selection(self):
        fitnessmass = [ind.objectives[0] for ind in self._pop]
        decreaseindexes = np.argsort(fitnessmass)[::-1]
        fitnessesprob = [0] * len(self._pop)
        for i in range(0, len(self._pop)):
            fitnessesprob[decreaseindexes[i]] = (2.0 * (i + 1.0)) / (len(self._pop) * (len(self._pop) + 1))

        selected_indexes = []
        for j in range(len(self._pop) * 2):
            randomnum = randint(0, 10000)
            randomnum = randomnum / 10000.0
            check = 0
            for i in range(0, len(self._pop)):
                check += fitnessesprob[i]
                if check >= randomnum:
                    selected_indexes.append(self._pop[i])
                    break
                elif i == len(self._pop) - 1:
                    selected_indexes.append(self._pop[i])

        return selected_indexes

    def tournament_selection(self, group_size):

        selected = []

        for j in range(len(self._pop) * 2):

            tournir = [randint(0, len(self._pop) - 1) for i in range(group_size)]
            fitnessobjfromtour = [self._pop[tournir[i]].objectives[0] for i in range(group_size)]

            if StaticStorage.task.goal == "minimise":
                selected.append(self._pop[tournir[np.argmin(fitnessobjfromtour)]])
            else:
                selected.append(self._pop[tournir[np.argmax(fitnessobjfromtour)]])

        return selected

    def reproduce(self, selected, pop_size):

        children = []

        for pair_index in range(0, len(selected), 2):
            p1 = selected[pair_index]
            p2 = selected[pair_index + 1]

            child_gen = self.crossover(p1.genotype, p2.genotype, self.params.crossover_rate)
            child_gen = self.mutation(child_gen, self.params.mutation_rate, self.params.mutation_value_rate)
            child = DE_.Individ(genotype=child_gen)
            children.append(child)

        return children
