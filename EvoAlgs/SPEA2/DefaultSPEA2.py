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

        EvoAnalytics.pop_size=self.params.pop_size
        EvoAnalytics.set_params()

        gen = 0

        with open('out.txt', 'w') as out:
            out.write('{}\n'.format("archive"))


        while gen < self.params.max_gens:


            print("GEN!!!!! ", gen)


            self.fitness(gen)

            [EvoAnalytics.save_cantidate(gen, ind.objectives, ind.genotype.genotype_array, ind.referenced_dataset) for ind in self._pop]

            #####Visualize best individuals
            #EvoAnalytics.create_chart(gen, data_for_analyze='obj', chart_for_gif=True)
            #EvoAnalytics.create_chart(gen, data_for_analyze='gen_len', chart_for_gif=True)
            #####Visualize best individuals

            #individuals=[[int(ind.genotype.genotype_array[j]) for j in range(len(ind.genotype.genotype_array))] for ind in self._pop]

            #self.print_func(individuals=individuals, fitnesses=fitnesses, num_of_pop=population_number)

            #for ind in self._pop:
                #print("ind in SPEA2", ind.genotype.genotype_array)

            self._archive = self.environmental_selection(self._pop, self._archive)

            with open('out.txt', 'a') as out:
                out.write('{}\n'.format(self._archive))
                out.write('{}\n'.format(len(self._archive)))


            best = sorted(self._archive, key=lambda p: mean_obj(p))[0]

            #best_for_print=  [i.genotype.genotype_array  for i in sorted(self._archive, key=lambda p: mean_obj(p))[:EvoAnalytics.num_of_best_inds_for_print]]


            #self.print_func(best_for_print, num_of_population=gen)


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

            #EvoAnalytics.create_chart(gen)

            gen += 1

        #To create one big picture with different plots for each generation
        #EvoAnalytics.chart_series_creator()
        EvoAnalytics.create_chart(data_for_analyze='obj',analyze_only_last_generation=False,chart_for_gif=True)
        EvoAnalytics.create_chart(data_for_analyze='gen_len', analyze_only_last_generation=False,chart_for_gif=True)

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
