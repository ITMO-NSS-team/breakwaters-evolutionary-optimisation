import copy
import itertools
import os
import random
import uuid
from itertools import chain

import numpy as np
from pyDOE import lhs
from scipy.stats.distributions import norm

from Breakers.BreakersUtils import BreakersUtils
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from EvoAlgs.BreakersEvo.BreakersParams import BreakersParams
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective
from Simulation.Results import WaveSimulationResult
from Visualisation.ModelVisualization import ModelsVisualization

# TODO refactor
len_range = [0, 3]
dir_range = [-50, 50]


def obtain_numerical_chromosome(task):
    chromosome = []
    for modification in task.possible_modifications:
        points_to_opt = task.mod_points_to_optimise[modification.breaker_id]
        points_to_encode = []
        prev_anchor = None
        for i in points_to_opt:
            anchor = modification.points[i + 1]
            prev_anchor = modification.points[i + 2]

            polar_coords = modification.points[i].point_to_relative_polar(anchor)

            # fill '-1' point to obtain next anchor
            modification.points[i].x = anchor.x + modification.points[i].x
            modification.points[i].y = anchor.y + modification.points[i].y

            real_angle = polar_coords["angle"]
            anchor_angle = anchor.point_to_relative_polar(prev_anchor)["angle"]
            relative_angle = ((real_angle - anchor_angle) + 360) % 360
            points_to_encode.append([polar_coords["length"], relative_angle])

        chromosome.append(list(chain.from_iterable(points_to_encode)))
    return list(chain.from_iterable(chromosome))


def fitness_function_of_single_objective_optimization(model, task, ind):
    pre_simulated_results = None

    proposed_breakers = BreakersEvoUtils.build_breakers_from_genotype(ind, task, model.domain.model_grid)

    objectives = []

    base_objectives = _calculate_reference_objectives(model, task)

    combined_breakers_for_cost_estimation = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers,
                                                                                            proposed_breakers)

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


'''

def print_individuals(model, task, individuals,fitnesses,num_of_pop,goal="minimization"):

    num_of_best_individuals = EvoAnalytics.num_of_best_inds_for_print
    if goal == "minimization":
        indexes_of_individuals = np.argsort(fitnesses)[:num_of_best_individuals]
    else:
        indexes_of_individuals = np.argsort(fitnesses)[::-1][:num_of_best_individuals]


    for i, j in enumerate(indexes_of_individuals):

        print("num_of_pop_ind ", [num_of_pop, i])

        genotype = [int(g) for g in individuals[j]]

        proposed_breakers = BreakersEvoUtils.build_breakers_from_genotype(genotype, task, model.domain.model_grid)

        combined_breakers_for_cost_estimation = BreakersUtils.merge_breakers_with_modifications(
            model.domain.base_breakers, proposed_breakers)

        # if isinstance(obj, WaveHeightObjective):

        # for obj_ind, obj in enumerate(task.objectives):

        if sum([isinstance(obj, WaveHeightObjective) for obj in task.objectives]):

            simulation_result = model.run_simulation_for_constructions(proposed_breakers)

        else:

            simulation_result = WaveSimulationResult(
                hs=np.zeros(shape=(model.domain.model_grid.grid_y, model.domain.model_grid.grid_x)),
                configuration_label=EvoAnalytics.run_id)

        # simulation_result = model.run_simulation_for_constructions(proposed_breakers)

        all_breakers = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers,
                                                                       proposed_breakers)

        print("genitype", genotype)

        visualiser = ModelsVisualization(str(num_of_pop + 1) + "_" + str(i + 1),
                                         EvoAnalytics.run_id)

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                    model.domain.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    [[2]], dir="wave_gif_imgs", image_for_gif=True,
                                    population_and_ind_number=[num_of_pop,i])

'''


def print_individuals(model, task, pop, num_of_pop_ind=[]):
    # print("pop",pop)

    genotype = [int(round(g, 0)) for g in pop[0]]

    proposed_breakers = BreakersEvoUtils.build_breakers_from_genotype(genotype, task, model.domain.model_grid)

    combined_breakers_for_cost_estimation = BreakersUtils.merge_breakers_with_modifications(
        model.domain.base_breakers, proposed_breakers)

    # if isinstance(obj, WaveHeightObjective):

    # for obj_ind, obj in enumerate(task.objectives):

    if sum([isinstance(obj, WaveHeightObjective) for obj in task.objectives]):

        simulation_result = model.run_simulation_for_constructions(proposed_breakers)

    else:

        simulation_result = WaveSimulationResult(
            hs=np.zeros(shape=(model.domain.model_grid.grid_y, model.domain.model_grid.grid_x)),
            configuration_label=EvoAnalytics.run_id)

    # simulation_result = model.run_simulation_for_constructions(proposed_breakers)

    all_breakers = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers,
                                                                   proposed_breakers)

    # print("genitype",genotype)

    visualiser = ModelsVisualization(str(num_of_pop_ind[0] + 1) + "_" + str(num_of_pop_ind[1] + 1), EvoAnalytics.run_id)

    visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                model.domain.base_breakers,
                                StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                [[2]], dir="wave_gif_imgs", image_for_gif=True,
                                population_and_ind_number=num_of_pop_ind)


def calculate_objectives(model, task, pop, fromDE=False, check_intersections=False, num_of_pop_ind=[]):
    if check_intersections:

        genotype = [int(round(g, 0)) for g in pop[0]]
        proposed_breakers = BreakersEvoUtils.build_breakers_from_genotype(genotype, task, model.domain.model_grid)

        combined_breakers_for_cost_estimation = BreakersUtils.merge_breakers_with_modifications(
            model.domain.base_breakers, proposed_breakers)

        ####################################
        '''
        label = uuid.uuid4().hex
        simulation_result = WaveSimulationResult(
            hs=np.zeros(shape=(model.domain.model_grid.grid_y, model.domain.model_grid.grid_x)),
            configuration_label=label)
        label_to_reference = label

        all_breakers = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers,
                                                                           proposed_breakers)

        visualiser = ModelsVisualization(str(num_of_ind[0])+"_"+str(num_of_ind[1]), EvoAnalytics.run_id)

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                        model.domain.base_breakers,
                                        StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                        [[2]])
        '''
        ####################################

        obj = StructuralObjective(importance=1)

        obj_in_point = obj.get_obj_value(model.domain, combined_breakers_for_cost_estimation)

        # print("obj_in_point",obj_in_point)

        return obj_in_point

        # new_obj = obj.get_obj_value(model.domain, proposed_breakers)

    if model.computational_manager is not None and model.computational_manager.is_lazy_parallel:
        # cycle for the mass simulation run
        pre_simulated_results = []
        pre_simulated_results_idx = []

        for p_ind, p in enumerate(pop):

            if fromDE:
                genotype = [int(round(g, 0)) for g in p]
            else:
                genotype = [int(round(g, 0)) for g in p.genotype.genotype_array]

            proposed_breakers = BreakersEvoUtils.build_breakers_from_genotype(genotype, task, model.domain.model_grid)

            simulation_result = model.run_simulation_for_constructions(proposed_breakers)

            print("simulation result", simulation_result._hs)

            pre_simulated_results.append(simulation_result)
            pre_simulated_results_idx.append(simulation_result.configuration_label)

        finalised_values = model.computational_manager.finalise_execution()

        # process ids
        if len(finalised_values) > 0:
            for i, val in enumerate(finalised_values):
                label = val[0]
                hs = val[1]
                indices = [i for i, x in enumerate(pre_simulated_results_idx) if x == label]
                if len(indices) > 2:
                    print("STRANGE")
                for idx in indices:
                    pre_simulated_results[idx]._hs = hs

        for ps in pre_simulated_results:
            if ps._hs is None:
                print("NONE FOUND")
    else:
        pre_simulated_results = None

    if fromDE:
        all_objectives = []
        all_fitnesses = []
    for i_ind, p in enumerate(pop):
        label_to_reference = None

        if fromDE:
            genotype = [int(round(g, 0)) for g in p]
        else:
            genotype = [int(round(g, 0)) for g in p.genotype.genotype_array]

        proposed_breakers = BreakersEvoUtils.build_breakers_from_genotype(genotype, task, model.domain.model_grid)

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
                if model.computational_manager is None or not model.computational_manager.is_lazy_parallel:
                    simulation_result = model.run_simulation_for_constructions(proposed_breakers)
                else:
                    print("num of ind", i_ind)
                    try:
                        simulation_result = pre_simulated_results[i_ind]
                    except:
                        print("!")
                label_to_reference = simulation_result.configuration_label

                # print("simulation result",simulation_result._hs)

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

        if fromDE:

            objectives = [j for i in objectives for j in i]

            all_objectives.append(objectives)
            all_fitnesses.append(0.8 * objectives[0] + 0.9 * objectives[1] + 0.5 * objectives[2] + sum(objectives[3:]))

        else:
            p.objectives = list(itertools.chain(*objectives))

            p.referenced_dataset = label_to_reference

        if True:
            pass

            '''

            all_breakers = BreakersUtils.merge_breakers_with_modifications(model.domain.base_breakers,
                                                                           proposed_breakers)

            if fromDE:
                visualiser = ModelsVisualization(str(num_of_pop_ind[0]) + "_" + str(num_of_pop_ind[1]), EvoAnalytics.run_id)

                visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                            model.domain.base_breakers,
                                            StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                            objectives, image_for_gif=True, population_and_ind_number=num_of_pop_ind)
            else:
                visualiser = ModelsVisualization(f'swan_{simulation_result.configuration_label}', EvoAnalytics.run_id)

                visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers, model.domain.base_breakers,
                                            StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                            objectives,image_for_gif=False,population_and_ind_number=num_of_pop_ind)

            '''
    if fromDE:
        return all_fitnesses, all_objectives


def _calculate_reference_objectives(model, task):
    objectives = []
    simulation_result = None
    for obj_ind, obj in enumerate(task.objectives):
        if isinstance(obj, (CostObjective, NavigationObjective, StructuralObjective)):
            # TODO expensive check can be missed? investigate
            new_obj = obj.get_obj_value(model.domain, model.domain.base_breakers)
            objectives.append(new_obj)

        if isinstance(obj, WaveHeightObjective):

            if model.computational_manager is not None and model.computational_manager.is_lazy_parallel:
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers)
                values = model.computational_manager.finalise_execution()
                # process ids
                if len(values) > 0:
                    for i, val in enumerate(values):
                        label = val[0]
                        hs = val[1]
                        simulation_result._hs = hs
            else:
                simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers)

            new_obj = (obj.get_obj_value(model.domain, model.domain.base_breakers, simulation_result))
            objectives.append(new_obj)

    if not os.path.isdir(f'img/{EvoAnalytics.run_id}/swan_default.png') and simulation_result is not None:
        visualiser = ModelsVisualization(f'swan_default', EvoAnalytics.run_id)
        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), model.domain.base_breakers,
                                    model.domain.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    objectives)
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
                obj_val = objective.get_obj_value(StaticStorage.exp_domain,
                                                  BreakersEvoUtils.build_breakers_from_genotype(
                                                      genotype_array,
                                                      StaticStorage.task, StaticStorage.exp_domain.model_grid))
                if obj_val >= 0 and isinstance(objective, NavigationObjective):
                    is_bad = True
                    print("Unsuccesful crossover N")

                    continue
                if obj_val > 0 and isinstance(objective, StructuralObjective):
                    is_bad = True
                    print("Unsuccesful crossover S")
            if not is_bad: new_individ.genotype_array = copy.copy(genotype_array)
            iter += 1

    return new_individ


def mutation(individ, rate, mutation_value_rate):
    new_individ = BreakersParams(copy.deepcopy(individ.genotype_array))

    if random.random() >= 1 - rate:

        strict_objectives = [NavigationObjective(), StructuralObjective()]
        is_bad = True
        iter = 0

        for _ in range(0,
                       random.randint(1, int(round(len(individ.genotype_array) / 2)))):  # number of mutations
            is_bad = True
            while is_bad and iter < 50:
                print(f'MUTATION{iter}')

                param_to_mutate = random.randint(0, int(round(len(individ.genotype_array) / 2 - 1)))
                mutation_ratio = abs(np.random.RandomState().normal(5, 1.5, 1)[0])
                mutation_ratio_dir = abs(np.random.RandomState().normal(10, 5, 1)[0])

                sign = 1 if random.random() < 0.5 else -1

                genotype_array = copy.copy(new_individ.genotype_array)

                len_ind = param_to_mutate * 2
                dir_ind = param_to_mutate * 2 + 1
                genotype_array[len_ind] += sign * mutation_ratio
                genotype_array[len_ind] = abs(genotype_array[len_ind])
                genotype_array[dir_ind] += sign * mutation_ratio_dir
                genotype_array[dir_ind] = min(genotype_array[dir_ind], dir_range[0])
                genotype_array[dir_ind] = max(genotype_array[dir_ind], - dir_range[1])

                is_bad = False
                for objective in strict_objectives:
                    obj_val = objective.get_obj_value(StaticStorage.exp_domain,
                                                      BreakersEvoUtils.build_breakers_from_genotype(
                                                          genotype_array, StaticStorage.task,
                                                          StaticStorage.exp_domain.model_grid))

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
    samples_grid = lhs(StaticStorage.genotype_length, size * 3, 'center')

    for i in range(0, StaticStorage.genotype_length):
        if i % 2 == 0:
            par_range = len_range
            par_scale = 1
        else:
            par_range = dir_range
            par_scale = 50

        # TODO better sampling
        samples_grid[:, i] = (norm(loc=np.mean(par_range), scale=par_scale).ppf(samples_grid[:, i]))

    population = [BreakersParams(genotype) for genotype in samples_grid]
    population_new = []

    strict_objectives = [NavigationObjective(), StructuralObjective()]
    for ind in population:
        bad = False
        for objective in strict_objectives:
            obj_val = objective.get_obj_value(StaticStorage.exp_domain,
                                              BreakersEvoUtils.build_breakers_from_genotype(ind.genotype_array,
                                                                                            StaticStorage.task))
            if obj_val is None:
                bad = True
                break
        if not bad:
            population_new.append(ind)
        if len(population_new) == size: break

    return population_new


def initial_pop_random(size, **kwargs):
    population_new = []
    for _ in range(0, size):

        strict_objectives = [NavigationObjective(), StructuralObjective()]
        while len(population_new) < size:
            genotype = np.zeros(StaticStorage.genotype_length)
            for j, g in enumerate(genotype):
                if j % 2 == 0:
                    genotype[j] = random.randint(0, 3)


                else:
                    genotype[j] = random.randint(-3, 3) * 15

            is_bad = False
            for objective in strict_objectives:
                obj_val = objective.get_obj_value(StaticStorage.exp_domain,
                                                  BreakersEvoUtils.build_breakers_from_genotype(genotype,
                                                                                                StaticStorage.task,
                                                                                                StaticStorage.exp_domain.model_grid))
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
