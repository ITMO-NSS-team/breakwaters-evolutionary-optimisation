import copy
from math import sqrt

import numpy as np
import math

from EvoAlgs.SPEA2.SPEA2 import SPEA2
from EvoAlgs.EvoAnalytics import EvoAnalytics


class DefaultSPEA2(SPEA2):
    def solution(self, verbose=True, **kwargs):
        archive_history = []
        history = SPEA2.ErrorHistory()

        EvoAnalytics.num_of_generations=self.params.max_gens
        EvoAnalytics.num_of_rows=math.ceil(EvoAnalytics.num_of_generations / EvoAnalytics.num_of_cols)
        #EvoAnalytics.num_of_rows=4
        EvoAnalytics.pop_size=self.params.pop_size
        EvoAnalytics.set_params()

        print("num of gen",EvoAnalytics.num_of_generations)
        print("num of rows",EvoAnalytics.num_of_rows)
        print("pop size",EvoAnalytics.pop_size)



        gen = 0
        while gen < self.params.max_gens:

            #print("gener evo an", EvoAnalytics.gener)
            #print("maxgens",EvoAnalytics.num_of_generations)
            #print("num_of_rows",EvoAnalytics.num_of_rows )
            self.fitness()

            [EvoAnalytics.save_cantidate(gen, ind.objectives, ind.genotype.genotype_array, ind.referenced_dataset) for ind in self._pop]

            #EvoAnalytics.chart_series_creator()

            self._archive = self.environmental_selection(self._pop, self._archive)
            best = sorted(self._archive, key=lambda p: mean_obj(p))[0]

            last_fit = history.last().fitness_value
            if last_fit > mean_obj(best):
                best_gens = best.genotype

                if verbose:
                    if 'print_fun' in kwargs:
                        kwargs['print_fun'](best, gen)
                    else:
                        print_new_best_individ(best, gen)

                history.add_new(best_gens, gen, mean_obj(best), 0)

            selected = self.selected(self.params.pop_size, self._archive)
            self._pop = self.reproduce(selected, self.params.pop_size)

            to_add = copy.deepcopy(self._archive + self._pop)
            self.objectives(to_add)
            archive_history.append(to_add)

            EvoAnalytics.create_chart(gen)

            gen += 1


        #EvoAnalytics.chart_series_creator()

        return history, archive_history


def mean_obj(individ):
    return np.mean(individ.objectives)


def print_new_best_individ(best, gen_index):
    print("new best: ", round(best.fitness(), 5), round(best.genotype.drf, 2),
          round(best.genotype.cfw, 6),
          round(best.genotype.stpm, 6),
          0,
          mean_obj(best))
    print(gen_index)
