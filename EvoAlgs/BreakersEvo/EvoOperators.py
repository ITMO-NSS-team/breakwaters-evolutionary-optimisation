import random
import uuid
from itertools import chain

import numpy as np
from pyDOE import lhs
from scipy.stats.distributions import norm

from Breakers.Breaker import xy_to_points, Breaker
from Breakers.BreakersUtils import BreakersUtils
from Configuration.Domains import SochiHarbor
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from EvoAlgs.BreakersEvo.BreakersParams import BreakersParams
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Optimisation.OptimisationTask import OptimisationTask
from Simulation.ModelVisualization import ModelsVisualization
from Simulation.Results import WaveSimulationResult
from EvoAlgs.EvoAnalytics import EvoAnalytics
import copy

import itertools

# TODO remove hack

exp_domain = SochiHarbor()

base_modifications_for_tuning = [
    Breaker('mod1', list(map(xy_to_points, [[-1, -1], [-1, -1], [33, 22], [42, 17]])), 0, 'Ia'),
    Breaker('mod2_top', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 32], [50, 39]])), 0, 'II'),
    Breaker('mod2_bottom', list(map(xy_to_points, [[-1, -1], [-1, -1], [50, 39]])), 0, 'II'),
    Breaker('mod3long', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 32], [67, 35]])), 0.9, 'IIIa'),
    Breaker('mod3short', list(map(xy_to_points, [[-1, -1], [-1, -1], [63, 38], [67, 39]])), 0.9, 'IIIb'),
    Breaker('mod_add', list(map(xy_to_points, [[-1, -1], [-1, -1], [56, 42]])), 0.9, '-'),
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
    for p_ind, p in enumerate(pop):
        label_to_reference = None
        genotype = [int(round(g, 0)) for g in p.genotype.genotype_array]

        proposed_breakers = _build_breakers_from_genotype(genotype, task)
        objectives = []

        base_objectives = _calculate_reference_objectives(model, task)

        combined_breakers_for_cost_estimation = BreakersUtils.merge_breakers_with_modifications(
            model.domain.base_breakers, proposed_breakers)

        for obj_ind, obj in enumerate(task.objectives):
            if isinstance(obj, (CostObjective, NavigationObjective, StructuralObjective)):
                # TODO expensive check can be missed? investigate
                if not isinstance(obj, StructuralObjective):
                    new_obj = obj.get_obj_value(model.domain, combined_breakers_for_cost_estimation)
                else:
                    new_obj = obj.get_obj_value(model.domain, proposed_breakers)

                if isinstance(obj, CostObjective):
                    new_obj = (new_obj - base_objectives[obj_ind]) / base_objectives[obj_ind] * 100
                if isinstance(obj, NavigationObjective):
                    new_obj = -(new_obj - base_objectives[obj_ind]) / base_objectives[obj_ind] * 100
                if isinstance(obj, StructuralObjective):
                    new_obj = new_obj - base_objectives[obj_ind]

                objectives.append([new_obj])

            if isinstance(obj, WaveHeightObjective):
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                           proposed_breakers)
                label_to_reference = simulation_result.configuration_label
                new_obj = (obj.get_obj_value(model.domain, proposed_breakers, simulation_result))

                # for 3 points it is list
                new_obj = [(x1 - x2) / x2 * 100 for (x1, x2) in zip(new_obj, base_objectives[obj_ind])]

                objectives.append(new_obj)
            else:
                if len(task.objectives) < 4:
                    label = uuid.uuid4().hex
                    simulation_result = WaveSimulationResult(
                        hs=np.zeros(shape=(model.domain.model_grid.grid_y, model.domain.model_grid.grid_x)),
                        configuration_label=label)
                    label_to_reference = label

        print(objectives)
        if True:
            all_breakers = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers,
                                                                           proposed_breakers)

            visualiser = ModelsVisualization(f'swan_{simulation_result.configuration_label}', EvoAnalytics.run_id)

            visualiser.simple_visualise(simulation_result.hs, all_breakers, model.domain.base_breakers,
                                        exp_domain.fairways, exp_domain.target_points, objectives)
        p.objectives = list(itertools.chain(*objectives))

        p.referenced_dataset = label_to_reference


def _calculate_reference_objectives(model, task):
    # <class 'list'>: [0, 651.0, -50.0, [100.0, 150.0, 160.0]]
    objectives = []
    for obj_ind, obj in enumerate(task.objectives):
        if isinstance(obj, (CostObjective, NavigationObjective, StructuralObjective)):
            # TODO expensive check can be missed? investigate
            new_obj = obj.get_obj_value(model.domain, model.domain.base_breakers)
            objectives.append(new_obj)

        if isinstance(obj, WaveHeightObjective):
            simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers,
                                                                       model.domain.base_breakers)
            new_obj = (obj.get_obj_value(model.domain, model.domain.base_breakers, simulation_result))
            objectives.append(new_obj)
    return objectives


def crossover(p1, p2, rate):
    if random.random() >= 1 - rate:
        return p1

    strict_objectives = [NavigationObjective(), StructuralObjective()]
    is_bad = True
    iter = 0
    new_individ = BreakersParams(copy.deepcopy(p1.genotype_array))
    for gen_ind in range(0, len(p1.genotype_array), 2):
        is_bad = True

        while is_bad and iter < 50:
            print(f'CROSSOVER {iter}')

            angle_parent_id = random.randint(0, 1)

            part1_rate = abs(random.random())
            part2_rate = 1 - part1_rate

            genotype_array = copy.copy(new_individ.genotype_array)

            len_ind = gen_ind
            dir_ind = gen_ind + 1
            genotype_array[len_ind] = round(p1.genotype_array[len_ind] * part1_rate + p2.genotype_array[
                len_ind] * part2_rate)

            # av_angle = average_angles(
            #    [(p1.genotype_array[dir_ind] + 360) % 360, (p2.genotype_array[dir_ind] + 360) % 360])
            # if av_angle != 0:
            #    individ.genotype_array[dir_ind] = round(av_angle)
            # else:
            if angle_parent_id == 0:
                genotype_array[dir_ind] = round((p1.genotype_array[dir_ind] + 360) % 360)
            if angle_parent_id == 1:
                genotype_array[dir_ind] = round((p2.genotype_array[dir_ind] + 360) % 360)
            is_bad = False
            for objective in strict_objectives:
                obj_val = objective.get_obj_value(exp_domain,
                                                  BreakersEvoUtils.build_breakers_from_genotype(
                                                      genotype_array,
                                                      task))
                if obj_val >= 0 and isinstance(objective, NavigationObjective):
                    is_bad = True
                    print("Unsuccesful crossover N")

                    continue
                if obj_val > 0 and isinstance(objective, StructuralObjective):
                    is_bad = True
                    print("Unsuccesful crossover S")
            if not is_bad: new_individ.genotype_array = copy.copy(genotype_array)
            iter+=1


    return new_individ


def mutation(individ, rate, mutation_value_rate):
    new_individ = BreakersParams(copy.deepcopy(individ.genotype_array))

    if random.random() >= 1 - rate:

        strict_objectives = [NavigationObjective(), StructuralObjective()]
        is_bad = True
        iter = 0
        # new_individ = BreakersParams(individ.genotype_array)

        for _ in range(0,
                       random.randint(1, int(round(len(individ.genotype_array) / 2 - 1) / 2))):  # number of mutations
            is_bad = True
            while is_bad and iter < 50:
                print(f'MUTATION{iter}')

                param_to_mutate = random.randint(0, int(round(len(individ.genotype_array) / 2 - 1)))
                mutation_ratio = abs(np.random.RandomState().normal(2, 1, 1)[0])
                mutation_ratio_dir = abs(np.random.RandomState().normal(10, 5, 1)[0])

                sign = 1 if random.random() < 0.5 else -1

                genotype_array = copy.copy(new_individ.genotype_array)

                len_ind = param_to_mutate * 2
                dir_ind = param_to_mutate * 2 + 1
                genotype_array[len_ind] += sign * mutation_ratio
                genotype_array[len_ind] = abs(genotype_array[len_ind])
                genotype_array[dir_ind] += sign * mutation_ratio_dir
                genotype_array[dir_ind] = round((genotype_array[dir_ind] + 360) % 360)

                is_bad = False
                for objective in strict_objectives:
                    obj_val = objective.get_obj_value(exp_domain,
                                                      BreakersEvoUtils.build_breakers_from_genotype(
                                                          genotype_array,
                                                          task))

                    if obj_val >= 0 and isinstance(objective, NavigationObjective):
                        is_bad = True
                        print("Unsuccesful mutation N")

                        continue
                    if obj_val > 0 and isinstance(objective, StructuralObjective):
                        is_bad = True
                        print("Unsuccesful mutation S")

                        continue
                if not is_bad: new_individ.genotype_array = copy.copy(genotype_array)
                iter += 1
    return new_individ


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
                                              BreakersEvoUtils.build_breakers_from_genotype(ind.genotype_array,
                                                                                            task))
            if obj_val is None:
                bad = True
                break
        if not bad:
            population_new.append(ind)
        if len(population_new) == size: break

    return population_new


def initial_pop_random(size, **kwargs):
    population_new = []
    for i in range(0, size):

        strict_objectives = [NavigationObjective(), StructuralObjective()]
        while len(population_new) < size:
            genotype = np.zeros(NPARAMS)
            for j, g in enumerate(genotype):
                if j % 2 == 0:
                    genotype[j] = random.randint(0, 3)
                else:
                    genotype[j] = random.randint(0, 359)

            is_bad = False
            for objective in strict_objectives:
                obj_val = objective.get_obj_value(exp_domain,
                                                  BreakersEvoUtils.build_breakers_from_genotype(genotype,
                                                                                                task))
                if obj_val >= 0 and isinstance(objective, NavigationObjective):
                    is_bad = True
                    # print("Unsuccesful init N")
                    continue
                if obj_val > 0 and isinstance(objective, StructuralObjective):
                    is_bad = True
                    # print("Unsuccesful init S")
                    continue

            if not is_bad:
                population_new.append(BreakersParams(copy.deepcopy(genotype)))

    return population_new
