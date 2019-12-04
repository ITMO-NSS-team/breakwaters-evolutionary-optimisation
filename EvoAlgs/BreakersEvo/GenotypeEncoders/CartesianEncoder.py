from abc import abstractmethod
import copy
import random
from CommonUtils.StaticStorage import StaticStorage
import numpy as np
from EvoAlgs.BreakersEvo.GenotypeEncoders.GenotypeEncoder import DirectGenotypeEncoder


class CartesianGenotypeEncoder(DirectGenotypeEncoder):

    def __init__(self):
        self.min_for_init = [-3, -3]
        self.max_for_init = [3, 3]
        self.genotype_mask = None

    def parameterized_genotype_to_breakers(self, genotype, task, grid):
        gen_id = 0
        new_modifications = []

        for modification in task.possible_modifications:

            if modification.breaker_id in task.mod_points_to_optimise:
                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

                for point_ind in point_ids_to_optimise_in_modification:
                    modification.points[point_ind].x = genotype[gen_id]
                    modification.points[point_ind].x = genotype[gen_id + 1]
                    gen_id += 2

            new_modifications.append(modification)
        return new_modifications

    def breakers_to_parameterized_genotype(self, breakers, task, grid):
        chromosome = []

        for modification in task.possible_modifications:

            if modification.breaker_id in task.mod_points_to_optimise:

                breaker = [b for b in breakers if b.breaker_id == modification.breaker_id][0]

                point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

                prev_anchor = modification.points[max(point_ids_to_optimise_in_modification) + 2]

                for point_ind in point_ids_to_optimise_in_modification:
                    if modification.points[max(point_ids_to_optimise_in_modification)].x == -1:
                        x = prev_anchor.x
                        y = prev_anchor.y
                        prev_anchor = anchor_point
                        anchor_point = modification.points[point_ind]
                    else:
                        last_point = breaker.points[max(point_ids_to_optimise_in_modification)]
                        x = last_point.x
                        y = last_point.y

                        prev_anchor = anchor_point
                        anchor_point = last_point
                    chromosome.append(x)
                    chromosome.append(y)
        return chromosome
