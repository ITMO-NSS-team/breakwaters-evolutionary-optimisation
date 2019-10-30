from EvoAlgs.DE.base import *
import numpy as np
from EvoAlgs.EvoAnalytics import EvoAnalytics
import math
from tqdm import tqdm

class DEIterator:
    def __init__(self, de):
        self.de = de
        self.population = de.init()
        self.fitness, self.objectives = de.evaluate(self.population, 0)
        # self.fitness=de.evaluate(self.population, 0)

        self.best_fitness = min(self.fitness)
        self.index_of_ind = 0
        # if de.save_gif_images:
        # de.print_individuals_with_best_fitness(self.population, self.fitness, 0)

        EvoAnalytics.num_of_best_inds_for_print = 5
        if de.goal == "minimization":
            self.indexes_of_best_individuals = np.argsort(self.fitness)[:EvoAnalytics.num_of_best_inds_for_print]
        else:
            self.indexes_of_best_individuals = np.argsort(self.fitness)[::-1][:EvoAnalytics.num_of_best_inds_for_print]

        # print("indexes",self.indexes_of_best_individuals)

        self.best_idx = np.argmin(self.fitness)
        # F and CR control parameters
        self.f, self.cr = dither(de.mutation_bounds, de.crossover_bounds)
        # Last mutant created
        self.mutant = None
        # Index of the last target vector used for mutation/crossover
        self.idx_target = 0
        # Current iteration of the algorithm (it is incremented
        # only when all vectors of the population are processed)
        self.iteration = 0

    def __iter__(self):
        de = self.de
        # This is the main DE loop. For each vector (target vector) in the
        # population, a mutant is created by combining different vectors in
        # the population (depending on the strategy selected). If the mutant
        # is better than the target vector, the target vector is replaced.
        while self.iteration < self.de.maxiters:
            # Compute values for f and cr in each iteration
            # de.print_individuals_with_best_fitness(self.population, self.fitness, self.iteration)
            self.f, self.cr = self.calculate_params()

            mutants = []
            for self.idx_target in range(de.popsize):
                # Create a mutant using a base vector, and the current f and cr values
                mutants.append(self.create_mutant(self.idx_target))
            # Transfer mutants to calculate objectives function and get from this function container with 2 containers (first includes fitnesses and 2nd objectives)
            # Create some function which write this fit and obj-s to population static containers with fit and obj
            self.replace(mutants)
            # Yield the current state of the algorithm
            yield self
            self.iteration += 1

    def calculate_params(self):
        return dither(self.de.mutation_bounds, self.de.crossover_bounds)

    def create_mutant(self, i):
        if self.de.adaptive:
            # Use the params of the target vector
            dt = self.de.denormalize(self.population[i])
            self.f, self.cr = dt[-2:]
        self.mutant = self.de.mutant(i, self.population, self.f, self.cr)

        return self.mutant

    def replace(self, mutants):
        # mutant_fitness,obj = self.de.evaluate(np.asarray([mutant]), i)
        # return self.replacement(i, mutant, mutant_fitness, obj)
        mutant_fitness, obj = self.de.evaluate(np.asarray(mutants))

        return self.replacement(mutants, mutant_fitness, obj)
        # return self.replacement(i, mutant, mutant_fitness)

    def replacement(self, mutants, mutant_fitness, obj):

        for target_idx in range(len(mutants)):

            if (self.de.goal == "minimization" and mutant_fitness[target_idx] < self.best_fitness) or (
                    self.de.goal == "maximization" and mutant_fitness[target_idx] > self.best_fitness):
                self.best_fitnes = mutant_fitness[target_idx]
                self.best_idx = target_idx

            if (self.de.goal == "minimization" and mutant_fitness[target_idx] < self.fitness[target_idx]) or (
                    self.de.goal == "maximization" and mutant_fitness[target_idx] > self.fitness[target_idx]):
                self.population[target_idx] = mutants[target_idx]
                self.fitness[target_idx] = mutant_fitness[target_idx]
                self.objectives[target_idx] = obj[target_idx]
        return True
        # return False!

class DE:
    def __init__(self, fobj, print_func, bounds, mutation=(0.5, 1.0), crossover=0.7, maxiters=30,
                 self_adaptive=False, popsize=None, seed=None, dimensions=2, save_gif=True):

        self.save_gif_images = save_gif
        self.print_func = print_func
        self.goal = "minimization"
        self.memory = "static"
        print("bounds", bounds)
        self.adaptive = self_adaptive
        # Indicates the number of extra parameters in an individual that are not used for evaluating
        # If extra_params = d, discards the last d elements from an individual prior to evaluation.
        self.extra_params = 0
        # Convert crossover param to an interval, as in mutation. If min/max values in the interval are
        # different, a dither mechanism is used for crossover (although this is not recommended, but still supported)
        # TODO: Clean duplicate code

        self.crossover_bounds = crossover
        self.mutation_bounds = mutation

        if getattr(crossover, '__len__', None) is None:
            self.crossover_bounds = [crossover, crossover]

        if getattr(mutation, '__len__', None) is None:
            self.mutation_bounds = [mutation, mutation]

        # If self-adaptive, include mutation and crossover as two new variables
        bnd = list(bounds)
        if self_adaptive:
            bnd.append(self.mutation_bounds)
            bnd.append(self.crossover_bounds)
            self.extra_params = 2

        self._MIN = np.asarray(bnd[0], dtype='f8').T
        self._MAX = np.asarray(bnd[1], dtype='f8').T

        self._DIFF = [np.fabs(self._MAX[i] - self._MIN[i]) for i in range(len(self._MIN))]

        # self._MIN, self._MAX = np.asarray(bnd, dtype='f8').T
        # self._DIFF = np.fabs(self._MAX - self._MIN)
        # self.dims = len(bnd)
        # self.dims=fobj.dimensions

        self.dims = dimensions
        self.step_num=0
        self.fobj = fobj
        self.maxiters = maxiters
        if popsize is None:
            self.popsize = self.dims * 5
        else:
            self.popsize = popsize
        self.initialize_random_state(seed)
        self.name = 'DE'

    @staticmethod
    def initialize_random_state(seed):
        np.random.seed(seed)

    @staticmethod
    def crossover(target, mutant, probability):
        return binomial_crossover(target, mutant, probability)

    @staticmethod
    def mutate(target_idx, population, f):
        return rand1(target_idx, population, f)

    @staticmethod
    def repair(x):
        return random_repair(x)

    def init(self):

        # print("dims",self.dims)
        return self.random_init(self.popsize, self.dims)

    def check_constructions(self, new_ind):

        new_ind_denormalized = [i for i in self.denormalize([new_ind])[0]]
        return self.fobj(pop=[new_ind_denormalized], check_intersections=True)

    def random_init(self, popsize, dimensions):
        # print("dim-ions",dimensions)
        new_population = []

        for j in range(0, popsize):

            # num_of_attempt=0
            new_ind = [i for i in np.random.rand(dimensions)]
            # new_ind_denormalized = [i for i in self.denormalize([new_ind])[0]]

            # Check constructions
            # while self.fobj([new_ind_denormalized], check_intersections=True,num_of_pop_ind=[j,num_of_attempt]) is True:
            while self.check_constructions(new_ind) is True:
                # num_of_attempt+=1
                new_ind = [i for i in np.random.rand(dimensions)]
                # new_ind_denormalized = [i for i in self.denormalize([new_ind])[0]]

            new_population.append(new_ind)

        return np.array(new_population)
        # return np.random.rand(popsize, dimensions)

    def denormalize(self, population):

        #if not isinstance(population[0], (list, tuple)):
            #population=[population]

        return denormalize(self._MIN, self._DIFF, population)

    def mutant(self, target_idx, population, f, cr):
        # Create a mutant using a base vector
        trial = self.mutate(target_idx, population, f)
        # Repair the individual if a gene is out of bounds
        mutant = self.repair(self.crossover(population[target_idx], trial, cr))
        return mutant

    def evaluate(self, P, iteration=0):
        # Denormalize population matrix to obtain the scaled parameters

        # print("i",iteration)
        # print("P before denorm",P)
        PD = self.denormalize(P)

        if self.extra_params > 0:
            PD = PD[:, :-self.extra_params]

        return self.evaluate_denormalized(PD, iteration)

    def evaluate_denormalized(self, PD, index_of_ind):

        # print("index of ind",index_of_ind)

        if len(PD) > 1:
            if self.memory == "static":
                return self.fobj(pop=PD, multi_objective_optimization=False,population_number=self.step_num)
            elif self.memory == "dynamic":
                fit = []
                obj = []
                for i, ind in enumerate(PD):
                    fit_and_obj = self.fobj([ind], multi_objective_optimization=False, num_of_pop_ind=[self.step_num, i])
                    fit.append(fit_and_obj[0])
                    obj.append(fit_and_obj[1])

                return fit, obj
        else:
            fit_and_obj = self.fobj([PD[0]], multi_objective_optimization=False, num_of_pop_ind=[self.step_num + 1, index_of_ind])
            return [fit_and_obj[0]], fit_and_obj[1]

        '''
        if len(PD) > 1:
            return [self.fobj([ind], fromDE=True, num_of_pop_ind=[self.step_num, i]) for i, ind in enumerate(PD)]
        else:
            print("PPPPPPPPPDDDDDDDDDD",PD)
            return [self.fobj([ind], fromDE=True, num_of_pop_ind=[self.step_num + 1, index_of_ind]) for ind in PD]
        '''

    def iterator(self):
        return iter(DEIterator(self))

    def geniterator(self):
        it = self.iterator()
        iteration = 0
        for step in it:
            if step.iteration != iteration:
                iteration = step.iteration
                yield step

    '''
    def print_individuals_with_best_fitness(self, individuals, fitnesses, population_number):


        individuals=[self.denormalize([i]) for i in individuals]
        print("INDIVIDUALS AFTER DENORM",individuals)
        individuals=[[ int(round(j)) for j in i[0]] for i in individuals ]
        print("INDIVIDUALS AFTER ROUND", individuals)

        self.print_func(individuals=individuals,fitnesses=fitnesses, num_of_pop=population_number)

    '''

    def print_individuals_with_best_fitness(self, individuals, fitnesses, population_number):

        num_of_best_individuals = EvoAnalytics.num_of_best_inds_for_print
        if self.goal == "minimization":
            indexes_of_individuals = np.argsort(fitnesses)[:num_of_best_individuals]

            f = open("g.txt", "a+")
            f.write("population")

        else:
            indexes_of_individuals = np.argsort(fitnesses)[::-1][:num_of_best_individuals]

        denorm_individuals=[]
        for i, j in enumerate(indexes_of_individuals):
            print(j,individuals[j])
            denorm_individuals.append(self.denormalize([individuals[j]])[0])

        print("individuals after denormalize",denorm_individuals)

        self.print_func(pop=denorm_individuals, num_of_population=population_number)

        '''
        for i, j in enumerate(indexes_of_individuals):
            # print("num_of_pop_ind ", [population_number, i])

            self.print_func(self.denormalize([individuals[j]]), num_of_pop_ind=[population_number, i])
        '''


    def solve(self, show_progress=False):
        if show_progress:
            iterator = tqdm(self.iterator(), total=self.maxiters, desc='Optimizing ({0})'.format(self.name))
        else:
            iterator = self.iterator()

        # Analytics
        EvoAnalytics.num_of_generations = self.maxiters
        EvoAnalytics.num_of_rows = math.ceil(EvoAnalytics.num_of_generations / EvoAnalytics.num_of_cols)
        EvoAnalytics.pop_size = self.popsize
        EvoAnalytics.set_params()


        #with open('step_idx.txt', 'w') as out:
            #out.write('{}\n'.format("step"))


        for step_idx, step in enumerate(iterator):


            self.step_num=step_idx

            idx = step.best_idx
            P = step.population
            fitness = step.fitness
            obj = step.objectives

            [EvoAnalytics.save_cantidate(step.iteration, obj[i], ind) for i, ind in enumerate(P)]

            '''
            #Create charts during optimization pro#Create charts during optimizationcess
            if step_idx == 0:
                EvoAnalytics.create_chart(step.iteration, data_for_analyze='obj', chart_for_gif=True, first_generation=True)
                EvoAnalytics.create_chart(step.iteration, data_for_analyze='gen_len', chart_for_gif=True, first_generation=True)
            else:
                EvoAnalytics.create_chart(step.iteration, data_for_analyze='obj', chart_for_gif=True)
                EvoAnalytics.create_chart(step.iteration, data_for_analyze='gen_len', chart_for_gif=True)
            '''

            if self.save_gif_images:
                self.print_individuals_with_best_fitness(P, fitness, step_idx)

            if step.iteration > self.maxiters:

                if show_progress:
                    iterator.n = self.maxiters
                    iterator.refresh()
                    iterator.close()
                break

        EvoAnalytics.create_chart(data_for_analyze='obj', analyze_only_last_generation=False,
                                  chart_for_gif=True)
        EvoAnalytics.create_chart(data_for_analyze='gen_len', analyze_only_last_generation=False,
                                  chart_for_gif=True)

        return self.denormalize([P[idx].reshape(-1, 1)]), fitness[idx]

