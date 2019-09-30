from EvoAlgs.DE.base import *
import numpy as np
from Visualisation.ModelVisualization import ModelsVisualization
from EvoAlgs.EvoAnalytics import EvoAnalytics


class DEIterator:
    def __init__(self, de):
        self.de = de
        self.population = de.init()
        self.fitness = de.evaluate(self.population,0)
        self.best_fitness = min(self.fitness)
        self.index_of_ind=0
        if de.save_gif_images:
            de.print_individuals_with_best_fitness(self.population, self.fitness, 0)

        self.num_of_best_inds_for_print=5
        if de.goal == "minimization":
            self.indexes_of_best_individuals=np.argsort(self.fitness)[::-1][:self.num_of_best_inds_for_print]
        else:
            self.indexes_of_best_individuals = np.argsort(self.fitness)[:self.num_of_best_inds_for_print]

        #print("indexes",self.indexes_of_best_individuals)


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
            #de.print_individuals_with_best_fitness(self.population, self.fitness, self.iteration)
            self.f, self.cr = self.calculate_params()
            for self.idx_target in range(de.popsize):

                # Create a mutant using a base vector, and the current f and cr values
                mutant = self.create_mutant(self.idx_target)
                # Evaluate and replace if better
                self.replace(self.idx_target, mutant)
                # Yield the current state of the algorithm
                yield self
            self.iteration += 1

    def calculate_params(self):
        return dither(self.de.mutation_bounds, self.de.crossover_bounds)

    def create_mutant(self, i):
        # Simple self-adaptive strategy, where the F and CR control
        # parameters are inherited from the base vector.
        if self.de.adaptive:
            # Use the params of the target vector
            dt = self.de.denormalize(self.population[i])
            self.f, self.cr = dt[-2:]
        self.mutant = self.de.mutant(i, self.population, self.f, self.cr)
        return self.mutant

    def replace(self, i, mutant):
        mutant_fitness, = self.de.evaluate(np.asarray([mutant]),i)
        return self.replacement(i, mutant, mutant_fitness)

    def replacement(self, target_idx, mutant, mutant_fitness):
        if mutant_fitness < self.best_fitness:
            self.best_fitness = mutant_fitness
            self.best_idx = target_idx
        if mutant_fitness < self.fitness[target_idx]:
            self.population[target_idx] = mutant
            self.fitness[target_idx] = mutant_fitness
            return True
        return False


class PDEIterator(DEIterator):
    def __init__(self, de):
        super().__init__(de)
        self.mutants = np.zeros((de.popsize, de.dims))

    def create_mutant(self, i):
        mutant = super().create_mutant(i)
        # Add to the mutants population for parallel evaluation (later)
        # self.mutants.append(mutant)
        self.mutants[i, :] = mutant
        return mutant

    def replace(self, i, mutant):
        # Do not analyze after having the whole population (wait until the last individual)
        if i == self.de.popsize - 1:
            # Evaluate the whole new population (class PDE implements a parallel version of evaluate)
            mutant_fitness = self.de.evaluate(self.mutants,i)
            for j in range(self.de.popsize):
                super().replacement(j, self.mutants[j], mutant_fitness[j])


class DE:
    def __init__(self,fobj,print_func,bounds, mutation=(0.5, 1.0), crossover=0.7, maxiters=30,
                 self_adaptive=False, popsize=None, seed=None,dimensions=2,save_gif=True):

        self.save_gif_images=save_gif
        self.print_func=print_func
        self.goal="minimization"
        print("bounds",bounds)
        self.adaptive = self_adaptive
        self.step_num=0
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

        self._MIN=np.asarray(bnd[0], dtype='f8').T
        self._MAX=np.asarray(bnd[1], dtype='f8').T


        self._DIFF = [np.fabs(self._MAX[i] - self._MIN[i]) for i in range(len(self._MIN))]


        #self._MIN, self._MAX = np.asarray(bnd, dtype='f8').T
        #self._DIFF = np.fabs(self._MAX - self._MIN)
        #self.dims = len(bnd)
        #self.dims=fobj.dimensions

        self.dims=dimensions

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


        #print("dims",self.dims)
        return self.random_init(self.popsize, self.dims)

    def random_init(self,popsize, dimensions):
        # print("dim-ions",dimensions)
        new_population=[]

        for j in range(0,popsize):
            #new_ind = [i for i in np.random.rand(dimensions)]
            #new_ind = self.denormalize([[i for i in np.random.rand(dimensions)]])
            num_of_attempt=0
            new_ind=[i for i in np.random.rand(dimensions)]
            new_ind_denormalized = [i for i in self.denormalize([new_ind])[0]]
            while self.fobj([new_ind_denormalized], check_intersections=True,num_of_pop_ind=[j,num_of_attempt]) is True:
                num_of_attempt+=1

                new_ind=[i for i in np.random.rand(dimensions)]
                new_ind_denormalized = [i for i in self.denormalize([new_ind])[0]]

            new_population.append(new_ind)

        #if self.fobj([new_ind], check_intersections=True):
            #print("BAD_individ")
        #else:
            #print("Good individ")


        #print("randpop", np.random.rand(dimensions))
        print("new population",new_population)

        print("np.random",np.random.rand(popsize, dimensions))


        return np.array(new_population)
        #return np.random.rand(popsize, dimensions)

    def denormalize(self, population):

        return denormalize(self._MIN, self._DIFF, population)

    def mutant(self, target_idx, population, f, cr):
        # Create a mutant using a base vector
        trial = self.mutate(target_idx, population, f)
        # Repair the individual if a gene is out of bounds
        mutant = self.repair(self.crossover(population[target_idx], trial, cr))
        return mutant

    def evaluate(self, P,iteration):
        # Denormalize population matrix to obtain the scaled parameters

        #print("i",iteration)
        #print("P before denorm",P)
        PD = self.denormalize(P)
        #print("P after denorm", PD)
        if self.extra_params > 0:
            PD = PD[:, :-self.extra_params]
        return self.evaluate_denormalized(PD,iteration)

    def evaluate_denormalized(self, PD,index_of_ind):

        #print("PD",PD)
        #print("index of ind",index_of_ind)

        if len(PD)>1:
            return [self.fobj([ind], fromDE=True, num_of_pop_ind=[self.step_num, i]) for i,ind in enumerate(PD)]
        else:
            return [self.fobj([ind],fromDE=True,num_of_pop_ind=[self.step_num+1,index_of_ind]) for ind in PD]

    def iterator(self):
        return iter(DEIterator(self))

    def geniterator(self):
        it = self.iterator()
        iteration = 0
        for step in it:
            if step.iteration != iteration:
                iteration = step.iteration
                yield step

    def print_individuals_with_best_fitness(self,individuals,fitnesses,population_number):
        num_of_best_individuals=5
        if self.goal=="minimization":
            indexes_of_individuals=np.argsort(fitnesses)[::-1][:num_of_best_individuals]
        else:
            indexes_of_individuals = np.argsort(fitnesses)[:num_of_best_individuals]

        for i, j in enumerate(indexes_of_individuals):
            visualiser = ModelsVisualization(str(population_number) + "_" + str(j), EvoAnalytics.run_id)
            visualiser.Make_directory_for_gif_images()
            visualiser.Gif_images_saving(population_number,i)
        #for i,j in enumerate(indexes_of_individuals):

            #self.print_func([individuals[j]],num_of_pop_ind=[population_number,i])






    def solve(self, show_progress=False):
        if show_progress:
            from tqdm import tqdm
            iterator = tqdm(self.iterator(), total=self.maxiters, desc='Optimizing ({0})'.format(self.name))
        else:
            iterator = self.iterator()

        for step in iterator:



            idx = step.best_idx
            P = step.population
            fitness = step.fitness

            if self.save_gif_images:
                if step.iteration-1==self.step_num:
                    self.step_num+=1
                    self.print_individuals_with_best_fitness(P, fitness, self.step_num)

            if step.iteration > self.maxiters:
                if show_progress:
                    iterator.n = self.maxiters
                    iterator.refresh()
                    iterator.close()
                break

        return self.denormalize([P[idx].reshape(-1, 1)]), fitness[idx]


class PDE(DE):
    def __init__(self, fobj, bounds, mutation=(0.5, 1.0), crossover=0.7, maxiters=1000,
                 self_adaptive=False, popsize=None, seed=None, processes=None, chunksize=None):
        super().__init__(fobj, bounds, mutation, crossover, maxiters, self_adaptive, popsize, seed)
        from multiprocessing import Pool
        self.processes = processes
        self.chunksize = chunksize
        self.name = 'Parallel DE'
        self.pool = None
        if processes is None or processes > 0:
            self.pool = Pool(processes=self.processes)

    def iterator(self):
        it = PDEIterator(self)
        try:
            for data in it:
                yield data
        finally:
            if self.pool is not None:
                self.pool.terminate()

    def evaluate_denormalized(self, PD):
        if self.pool is not None:
            return list(self.pool.map(self.fobj, PD, chunksize=self.chunksize))
        else:
            return super().evaluate_denormalized(PD)