import copy
from math import sqrt

import numpy as np
import math

from EvoAlgs.SPEA2.SPEA2 import SPEA2
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from Visualisation.Visualiser import VisualiserState


class DefaultSPEA2(SPEA2):

    def _print_pop(self, label, lpop):
        print(label)
        for p in lpop:
            p_encoded = StaticStorage.genotype_encoder.breakers_to_parameterized_genotype(
                p.genotype.genotype,
                StaticStorage.task,
                StaticStorage.exp_domain.model_grid)
            print(p_encoded)

    def solution(self, verbose=True, **kwargs):
        extended_debug = True
        archive_history = []
        history = SPEA2.ErrorHistory()

        self.generation_number = 0

        if self.greedy_heuristic is not None:
            StaticStorage.genotype_encoder.genotype_mask = self.greedy_heuristic.init_mask(
                StaticStorage.genotype_encoder.genotype_mask, self.params.max_gens)

        while self.generation_number <= self.params.max_gens:
            print(f'Generation {self.generation_number}')
            self.visualiser.state = VisualiserState(self.generation_number)

            for individ in self._pop:
                individ.population_number=self.generation_number

            self.fitness()

            # [EvoAnalytics.save_cantidate(generation_number, ind.objectives, ind.genotype.genotype_array,
            #                             ind.referenced_dataset) for ind in self._pop]

            # self.visualiser.print_individuals([obj.objectives for obj in self._pop],
            #                                  [obj.simulation_result for obj in self._pop],
            #                                  [obj.genotype.get_genotype_as_breakers() for obj in self._pop],
            #                                  fitnesses=None, maxiters=self.params.max_gens)
            if extended_debug: self._print_pop("beforeA", self._pop)
            self._archive = self.environmental_selection(self._pop, self._archive)

            if extended_debug: self._print_pop("ARCH", self._archive)

            union = self._archive + self._pop
            selected = self.selected(self.params.pop_size, union)

            if extended_debug: self._print_pop("SEL", selected)

            self._pop = self.reproduce(selected, self.params.pop_size)

            if extended_debug: self._print_pop("REPR", self._pop)

            if self.greedy_heuristic is not None:
                StaticStorage.genotype_encoder.genotype_mask = self.greedy_heuristic.modify_mask(
                    StaticStorage.genotype_encoder.genotype_mask, self.generation_number)

            # EvoAnalytics.create_chart(gen)

            self.generation_number += 1

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
