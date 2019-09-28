# -*- coding: utf-8 -*-
import numpy as np


def binomial_crossover(target, mutant, cr):
    n = len(target)
    p = np.random.rand(n) < cr
    if not np.any(p):
        p[np.random.randint(0, n)] = True
    return np.where(p, mutant, target)


def random_sample(population, exclude, size=3):
    # Optimized version using numpy


    idxs = list(range(population.shape[0]))
    idxs.remove(exclude)
    sample = np.random.choice(idxs, size=size, replace=False)
    return population[sample]


def rand1(target_idx, population, f):
    a, b, c = random_sample(population, target_idx)
    return a + f * (b - c)


def my_generator(n,m):
    for i in range (n):
        for j in range (m):
            yield j

def denormalize(min_, diff, matrix):



    return np.split(np.asarray([min_[i]+j*diff[i] for k in range(len(matrix)) for i, j in zip(my_generator(int(len(matrix[k]) / len(min_)), len(min_)), matrix[k])]), len(matrix))

    #print("oooo3", np.split(np.asarray([min_[i] + j * diff[i] for k in range(len(matrix)) for i, j in zip(my_generator(int(len(matrix[k]) / len(min_)), len(min_)), matrix[k])],dtype='f8').T, len(matrix)))

    #print("ooo3",np.split(np.asarray([min_[i]+j*diff[i] for k in range(len(matrix)) for i, j in zip(my_generator(int(len(matrix[k]) / len(min_)), len(min_)), matrix[k])],dtype='f8').T, len(matrix))))
    #np.split(np.asarray(np.asarray([min_[i]+j*diff[i] for k in range(len(matrix)) for i, j in zip(my_generator(int(len(matrix[k]) / len(min_)), len(min_)), matrix[k])])), len(matrix)/len(min_))
    #print("ooo1",np.asarray([min_[i]+j*diff[i] for k in range(len(matrix)) for i, j in zip(my_generator(int(len(matrix[k]) / len(min_)), len(min_)), matrix[k])]))

'''
    for k in range(len(matrix)):
        for i, j in zip(my_generator(int(len(matrix[k]) / len(min_)), len(min_)), matrix[k]):

            print("MIN",min_[i])
            print("DIF",diff[i])
            print("j",j)
            print("LOOOOOk",min_[i]+j*diff[i])


    print("LenMin",min_)

    num_of_var=0
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
                if num_of_var==len(min_)-1:
                    num_of_var=0
                else:
                    num_of_var+=1
                print("LOOOOOk1",min_[num_of_var]+matrix[i][j]*diff[num_of_var])

    #[for i in range(len(matrix))]
    return min_ + matrix * diff
'''

def random_repair(x):
    # Detect the positions where the params is not valid
    loc = np.logical_or(x < 0, x > 1)
    # Count the number of invalid params
    count = np.sum(loc)
    # Replace each position where a True appears by a new random number in [0-1]
    if count > 0:
        np.place(x, loc, np.random.rand(count))
    return x


def bound_repair(x):
    return np.clip(x, 0, 1)


#def random_init(popsize, dimensions):

    #print("randpop",np.random.rand(dimensions))

    #return np.random.rand(popsize, dimensions)


def dither_from_interval(interval):
    low, up = min(interval), max(interval)
    if low == up:
        return low
    return np.random.uniform(low, up)


def dither(*intervals):
    return [dither_from_interval(interval) for interval in intervals]