import random
from itertools import chain

import numpy as np
from pyDOE import lhs
from scipy.stats.distributions import norm

from Breakers.Breaker import xy_to_points, Breaker
from Configuration.Domains import SochiHarbor
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from EvoAlgs.BreakersEvo.BreakersParams import BreakersParams
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from CommonUtils.MathUtils import average_angles

from Simulation.ConfigurationStrategies import ConfigurationInfo
from Simulation.ModelVisualization import ModelsVisualization
from Simulation.Results import WaveSimulationResult
from Simulation.СomputationalEnvironment import SwanComputationalManager, ComputationalManager

from Breakers.BreakersUtils import BreakersUtils

#TODO remove hack

exp_domain = SochiHarbor()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 39]])), 0, 'II'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 39]])), 0, 'II'),
    Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa'),
    Breaker('mod3short', list(map(xy_to_points, [[-1, -1], [-1, -1], [63, 38], [67, 39]])), 0.9, 'IIIb'),
    Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 38]])), 0.9, '-'),
]

mod_points_to_optimise = {  # order is important
    'mod1': [1, 0],
    'mod2_top': [1, 0],
    'mod2_bottom': [1, 0],
    'mod3long': [1, 0],
    'mod3short': [1, 0],
    'mod_add': [1, 0],
}

selected_modifications_for_tuning = base_modifications_for_tuning

objectives = [StructuralObjective(importance=1),
              CostObjective(importance=3),
              NavigationObjective(importance=1),
              WaveHeightObjective(importance=2)]

task = OptimisationTask(objectives, selected_modifications_for_tuning, mod_points_to_optimise, )

# TODO refactor
NPARAMS = 24
len_range = [0, 1]
dir_range = [0, 360]

exp_domain = SochiHarbor()


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
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers)

                new_obj = obj.get_obj_value(model.domain, proposed_breakers, simulation_result)
                objectives.append(new_obj)
        print(objectives)
        all_breakers = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers, proposed_breakers)

        visualiser = ModelsVisualization(f'swan_{simulation_result.configuration_label}')

        visualiser.simple_visualise(simulation_result.hs, all_breakers,
                                    exp_domain.fairways, exp_domain.target_points, objectives)
        p.objective = objectives


def crossover(p1, p2, rate):
    if random.random() >= rate:
        return p1

    strict_objectives = [NavigationObjective(), StructuralObjective()]
    is_bad = True
    iter = 0
    #while is_bad:
    angle_parent_id = random.randint(0, 1)
    part1_rate = abs(random.random())
    part2_rate = 1 - part1_rate
    individ = BreakersParams(p1.genotype_string)
    for gen_ind in range(0, len(p1.genotype_string), 2):
        len_ind = gen_ind
        dir_ind = gen_ind + 1
        individ.genotype_string[len_ind] = p1.genotype_string[len_ind] * part1_rate + p2.genotype_string[
            len_ind] * part2_rate

        # av_angle = average_angles(
        #    [(p1.genotype_string[dir_ind] + 360) % 360, (p2.genotype_string[dir_ind] + 360) % 360])
        # if av_angle != 0:
        #    individ.genotype_string[dir_ind] = round(av_angle)
        # else:
        if angle_parent_id == 0:
            individ.genotype_string[dir_ind] = round(p1.genotype_string[dir_ind])
        if angle_parent_id == 1:
            individ.genotype_string[dir_ind] = round(p2.genotype_string[dir_ind])
    is_bad = False
    for objective in strict_objectives:
        obj_val = objective.get_obj_value(exp_domain,
                                          BreakersEvoUtils.build_breakers_from_genotype(
                                              individ.genotype_string,
                                              task))
        if obj_val is None:
            is_bad = True
            print("Unsuccesful crossover")
            break
    iter += 1
    if iter > 25:
        return individ

    return individ


def mutation(individ, rate, mutation_value_rate):
    if random.random() >= rate:
        strict_objectives = [NavigationObjective(), StructuralObjective()]
        is_bad = True
        iter = 0
        new_individ = BreakersParams(individ.genotype_string)

        #while is_bad:
        param_to_mutate = random.randint(0, int(round(len(new_individ.genotype_string) / 2 - 1)))
        mutation_ratio = abs(np.random.RandomState().normal(1, 1, 1)[0])
        mutation_ratio_dir = abs(np.random.RandomState().normal(10, 5, 1)[0])

        sign = 1 if random.random() < 0.5 else -1

        child_params = BreakersParams(new_individ.genotype_string)
        len_ind = param_to_mutate * 2
        dir_ind = param_to_mutate * 2 + 1
        child_params.genotype_string[len_ind] += sign * mutation_ratio
        child_params.genotype_string[len_ind] = abs(child_params.genotype_string[len_ind])
        child_params.genotype_string[dir_ind] += sign * mutation_ratio_dir

        child_params.genotype_string[dir_ind] = abs((child_params.genotype_string[dir_ind] + 360) % 360)
        new_individ.genotype = child_params

        is_bad = False
        for objective in strict_objectives:
            obj_val = objective.get_obj_value(exp_domain,
                                              BreakersEvoUtils.build_breakers_from_genotype(
                                                  new_individ.genotype.genotype_string,
                                                  task))
            if obj_val is None:
                is_bad = True
                print("Unsuccesful mutation")
                print(child_params.genotype_string)
                break
        iter += 1

        if iter > 25:
            return new_individ

    return individ


def initial_pop_lhs(size, **kwargs):
    all_correct = False

    samples_grid = lhs(NPARAMS, size * 3, 'center')

    for i in range(0, NPARAMS):
        if i % 2 == 0:
            par_range = len_range
            par_scale = 1
        else:
            par_range = dir_range
            par_scale = 120

        # TODO better sampling
        samples_grid[:, i] = (norm(loc=np.mean(par_range), scale=par_scale).ppf(samples_grid[:, i]))

    population = [BreakersParams(genotype) for genotype in samples_grid]
    population_new = []

    strict_objectives = [NavigationObjective(), StructuralObjective()]
    for ind in population:
        bad = False
        for objective in strict_objectives:
            obj_val = objective.get_obj_value(exp_domain,
                                              BreakersEvoUtils.build_breakers_from_genotype(ind.genotype_string,
                                                                                            task))
            if obj_val is None:
                bad = True
                break
        if not bad:
            population_new.append(ind)
        if len(population_new) == size: break

    return population_new
