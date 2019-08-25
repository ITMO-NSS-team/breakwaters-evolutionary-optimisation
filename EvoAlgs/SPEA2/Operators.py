from EvoAlgs.BreakersEvo.EvoOperators import (
    initial_pop_lhs,
    initial_pop_random,
    crossover,
    mutation
)


class EvoOperators:
    def __init__(self, init_population, crossover, mutation):
        self.init_population = init_population
        self.crossover = crossover
        self.mutation = mutation


def default_operators():
    return EvoOperators(init_population=initial_pop_random, crossover=crossover, mutation=mutation)
