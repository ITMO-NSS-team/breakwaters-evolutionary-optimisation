import pickle
import random
from itertools import chain

import numpy as np
from pyDOE import lhs
from scipy.stats.distributions import norm

from itertools import chain
from Optimisation import OptimisationTask
from Optimisation.Objective import *
from EvoAlgs.BreakersEvo.BreakersParams import BreakersParams
from Configuration.Grid import BreakerPoint
from Simulation import WaveModel
from Simulation.WaveModel import SwanWaveModel
import csv
import uuid
from functools import partial
from Utils.MathUtils import average_angles

# TODO refactor
NPARAMS = 24
len_range = [0, 5]
dir_range = [0, 360]


def _obtain_numerical_chromosome(self, task):
    chromosome = []
    for modification in task.possible_modifications:
        points_to_opt = task.mod_points_to_optimise[modification.breaker_id]
        points_to_encode = []
        for i in points_to_opt:
            anchor = modification.points[i + 1]
            polar_coords = modification.points[i].point_to_relative_polar(anchor)

            # fill '-1' point for next anchor
            modification.points[i].x = anchor.x + modification.points[i].x
            modification.points[i].y = anchor.y + modification.points[i].y

            points_to_encode.append([polar_coords["length"], polar_coords["angle"]])

        chromosome.append(list(chain.from_iterable(points_to_encode)))
    return list(chain.from_iterable(chromosome))


def _build_breakers_from_genotype(genotype, task):
    gen_id = 0

    new_modifications = []

    for modification in task.possible_modifications:

        point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

        anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]

        for point_ind in point_ids_to_optimise_in_modification:
            modification.points[point_ind] = modification.points[point_ind].from_polar(genotype[gen_id],
                                                                                       genotype[gen_id + 1],
                                                                                       anchor_point)
            gen_id += 2
            anchor_point = modification.points[point_ind]
        new_modifications.append(modification)
    return new_modifications


def calculate_objectives(model, task, pop):
    for p in pop:

        genotype = [int(round(g, 0)) for g in p.genotype.genotype_string]

        proposed_breakers = _build_breakers_from_genotype(genotype, task)
        objectives = []
        for obj_ind, obj in enumerate(task.objectives):
            if isinstance(obj, (CostObjective, NavigationObjective, StructuralObjective)):
                # TODO expensive check can be missed? investigate
                new_obj = obj.get_obj_value(model.domain, proposed_breakers)
                if new_obj is None:
                    objectives = ([9999] * 4)
                    break
                objectives.append(new_obj)

            if isinstance(obj, WaveHeightObjective):
                # TODO read if already simulated
                # configuration_label = ''.join(str(g) for g in genotype)

                txt = []
                for pb in proposed_breakers:
                    for pbp in pb.points:
                        txt.append(str(int(pbp.x)))
                        txt.append(str(int(pbp.y)))
                txt_genotype = ",".join(txt)

                config_exists = False
                configuration_label = uuid.uuid4().hex

                if model.expensive:
                    with open('D://Projects//Sochi-prichal//breakwater-evo-opt//configs_catalog.csv',
                              mode='r', newline='') as csv_file:
                        sim_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
                        for row in sim_reader:
                            if row[1] == txt_genotype:
                                configuration_label = row[0]
                                config_exists = True
                                break
                    if not config_exists:
                        with open('D://Projects//Sochi-prichal//breakwater-evo-opt//configs_catalog.csv',
                                  mode='a', newline='') as csv_file:
                            sim_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                            sim_writer.writerow([f'{configuration_label}', txt_genotype])

                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers, configuration_label)
                new_obj = obj.get_obj_value(model.domain, proposed_breakers, simulation_result)
                objectives.append(new_obj)
        print(objectives)
        p.objective = objectives


def crossover(p1, p2, rate):
    if random.random() >= rate:
        return p1

    part1_rate = abs(random.random())
    part2_rate = 1 - part1_rate
    child_params = BreakersParams(p1.genotype_string)
    for gen_ind in range(0, len(p1.genotype_string), 2):
        len_ind = gen_ind
        dir_ind = gen_ind + 1
        child_params.genotype_string[len_ind] = p1.genotype_string[len_ind] * part1_rate + p2.genotype_string[
            len_ind] * part2_rate

        av_angle = average_angles([p1.genotype_string[dir_ind], p2.genotype_string[dir_ind]])
        if av_angle != 0:
            child_params.genotype_string[dir_ind] = av_angle
        else:
            child_params.genotype_string[dir_ind] = p2.genotype_string[dir_ind]

    return child_params


def mutation(individ, rate, mutation_value_rate):
    if random.random() >= rate:
        param_to_mutate = random.randint(0, int(round(len(individ.genotype_string) / 2 - 1)))
        mutation_ratio = abs(np.random.RandomState().normal(1, 1.5, 1)[0])
        mutation_ratio_dir = abs(np.random.RandomState().normal(10, 5, 1)[0])

        sign = 1 if random.random() < 0.5 else -1

        child_params = BreakersParams(individ.genotype_string)
        len_ind = param_to_mutate * 2
        dir_ind = param_to_mutate * 2 + 1
        child_params.genotype_string[len_ind] += individ.genotype_string[len_ind] * sign * mutation_ratio
        child_params.genotype_string[dir_ind] += ((individ.genotype_string[
                                                       dir_ind] * sign * mutation_ratio_dir) + 360) % 360
        individ.genotype = child_params

    return individ


# def default_initial_pop(size):
#    return [SWANParams.new_instance() for _ in range(size)]


def initial_pop_lhs(size, **kwargs):
    samples_grid = lhs(NPARAMS, size, 'center')

    for i in range(0, NPARAMS):
        if i % 2 == 0:
            par_range = len_range
            par_scale = 1
        else:
            par_range = dir_range
            par_scale = 120

        samples_grid[:, i] = (norm(loc=np.mean(par_range), scale=par_scale).ppf(samples_grid[:, i]))

    population = [BreakersParams(genotype) for genotype in samples_grid]

    return population
