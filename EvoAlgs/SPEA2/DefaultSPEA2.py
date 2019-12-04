import copy
from math import sqrt

import numpy as np
import math

from EvoAlgs.SPEA2.SPEA2 import SPEA2
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from Visualisation.Visualiser import VisualiserState


class DefaultSPEA2(SPEA2):

    def solution(self, verbose=True, **kwargs):
        archive_history = []
        history = SPEA2.ErrorHistory()

        generation_number = 0
        mask_index = 0

        if self.is_greedy:
            StaticStorage.genotype_encoder.genotype_mask[1:len(StaticStorage.genotype_encoder.genotype_mask)] = 1
            StaticStorage.genotype_encoder.genotype_mask[mask_index] = 0
            StaticStorage.genotype_encoder.genotype_mask[mask_index + 1] = 0

        while generation_number < self.params.max_gens:

            self.visualiser.state = VisualiserState(generation_number)

            self.fitness()

            # [EvoAnalytics.save_cantidate(generation_number, ind.objectives, ind.genotype.genotype_array,
            #                             ind.referenced_dataset) for ind in self._pop]

            # self.visualiser.print_individuals([obj.objectives for obj in self._pop],
            #                                  [obj.simulation_result for obj in self._pop],
            #                                  [obj.genotype.get_genotype_as_breakers() for obj in self._pop],
            #                                  fitnesses=None, maxiters=self.params.max_gens)

            self._archive = self.environmental_selection(self._pop, self._archive)

            # self.calculate_objectives(self._archive, self.visualiser)

            # best = sorted(self._archive, key=lambda p: mean_obj(p))[0]

            # last_fit = history.last().fitness_value
            # if last_fit > mean_obj(best):
            #    best_gens = best.genotype

            #   if verbose:
            #       if 'print_fun' in kwargs:
            #           kwargs['print_fun'](best, generation_number)
            #       else:
            #           print_new_best_individ(best, generation_number)
            #
            #   history.add_new(best_gens, generation_number, mean_obj(best), 0)

            selected = self.selected(self.params.pop_size, self._archive)
            self._pop = self.reproduce(selected, self.params.pop_size)

            if self.is_greedy & generation_number != 0 and generation_number % 3 == 0:
                StaticStorage.genotype_encoder.genotype_mask[mask_index - 2] = 1
                StaticStorage.genotype_encoder.genotype_mask[mask_index - 1] = 1
                StaticStorage.genotype_encoder.genotype_mask[mask_index] = 0
                StaticStorage.genotype_encoder.genotype_mask[mask_index + 1] = 0
                mask_index += 2
                genotype_mask_txt = ",".join([str(int(g)) for g in StaticStorage.genotype_encoder.genotype_mask])
                print(f'Current mask is [{genotype_mask_txt}]')

                if mask_index == len(StaticStorage.genotype_encoder.genotype_mask):
                    print("All greedy steps are done, genotype is fixed")
                    break

            to_add = copy.deepcopy(self._archive + self._pop)
            self.calculate_objectives(to_add, self.visualiser)

            archive_history.append(to_add)

            # EvoAnalytics.create_chart(gen)

            generation_number += 1

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
