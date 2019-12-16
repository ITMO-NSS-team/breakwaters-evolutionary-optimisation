import copy
from math import sqrt

import numpy as np
import math

from EvoAlgs.DE.DE_ import DE_
from EvoAlgs.EvoAnalytics import EvoAnalytics
from CommonUtils.StaticStorage import StaticStorage
from Visualisation.Visualiser import VisualiserState


class DefaultDE(DE_):

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
        self.generation_number = 0

        if self.greedy_heuristic is not None:
            StaticStorage.genotype_encoder.genotype_mask = self.greedy_heuristic.init_mask(
                StaticStorage.genotype_encoder.genotype_mask, self.params.max_gens)

        while self.generation_number <= self.params.max_gens:

            print(f'Generation {self.generation_number}')

            if self.visualiser is not None:
                self.visualiser.state = VisualiserState(self.generation_number)

            for individ in self._pop:
                individ.population_number = self.generation_number

            self.fitness()

            selected=self.tournament_selection(group_size=5)

            self._pop = self.reproduce(selected, self.params.pop_size)
            print("self. pop",self._pop)

            if extended_debug: self._print_pop("REPR", self._pop)

            if self.greedy_heuristic is not None:
                StaticStorage.genotype_encoder.genotype_mask = self.greedy_heuristic.modify_mask(
                    StaticStorage.genotype_encoder.genotype_mask, self.generation_number)

            self.generation_number += 1

        return 0