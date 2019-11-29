import copy
import itertools
import os
import random
import uuid
from itertools import chain
import copy

import numpy as np
from pyDOE import lhs
from scipy.stats.distributions import norm

from Breakers.BreakersUtils import BreakersUtils
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from EvoAlgs.BreakersEvo.BreakerIndividual import Individual
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import ObjectiveData, NavigationObjective, StructuralObjective, ConstraintComparisonType
from Visualisation.ModelVisualization import ModelsVisualization
from Simulation.Results import WaveSimulationResult

# TODO refactor
len_range = [0, 3]
dir_range = [-50, 50]


def calculate_objectives(model, task, visualiser, population):
    pre_simulated_results = model.computational_manager.prepare_simulations_for_population(population, model)

    # labels_to_reference_for_simulated_runs = []

    all_objectives = []

    for individ_index, individual in enumerate(population):
        # label_to_reference = None

        proposed_breakers = individual.genotype.get_as_breakers()
        objectives_values = []

        simulation_result = None
        base_simulation_result = None

        for obj_ind, obj in enumerate(task.objectives):
            if obj.is_simulation_required:
                base_simulation_result = model.run_simulation_for_constructions(model.domain.base_breakers)

                if model.computational_manager is None or not model.computational_manager.is_lazy_parallel:
                    simulation_result = model.run_simulation_for_constructions(proposed_breakers)
                else:
                    simulation_result = pre_simulated_results[individ_index]

                # label_to_reference = simulation_result.configuration_label

            objective_calculation_data = ObjectiveData(model.domain, proposed_breakers, model.domain.base_breakers,
                                                       simulation_result,
                                                       base_simulation_result)

            new_obj_value = obj.get_obj_value(objective_calculation_data)

            objectives_values.append([new_obj_value])

            if obj.is_simulation_required:
                if model.computational_manager is None or not model.computational_manager.is_lazy_parallel:
                    simulation_result = model.run_simulation_for_constructions(proposed_breakers)
                else:
                    try:
                        simulation_result = pre_simulated_results[individ_index]
                    except:
                        print("Simulated result not found in pre-simulated results")
                # label_to_reference = simulation_result.configuration_label

            else:
                if not any(obj.is_simulation_required for obj in task.objectives):
                    # stub for simulation results if no simulations needed
                    label = uuid.uuid4().hex
                    simulation_result = WaveSimulationResult(
                        hs=np.zeros(shape=(model.domain.model_grid.grid_y, model.domain.model_grid.grid_x)),
                        configuration_label=label)
                    # label_to_reference = None

        # un-list objectives
        objectives_values = list(itertools.chain(*objectives_values))

    all_objectives.append(objectives_values)

    # labels_to_reference_for_simulated_runs.append(label_to_reference)

    # simulation_result, all_breakers = build_decision(model, task, genotype)

    # simulation_results_store.append(copy.deepcopy(simulation_result))
    # all_breakers_store.append(copy.deepcopy(all_breakers))

    # [EvoAnalytics.save_cantidate(population_number, all_objectives[i], ind) for
    # i, ind in [g in individ.genotype for population]]

    # if not StaticStorage.multi_objective_optimization:
    #    visualiser.print_individuals(all_objectives, population_number, simulation_results_store, all_breakers_store,
    #                                 all_fitnesses, maxiters)
    #   return all_fitnesses, all_objectives
    # else:
    #    if subfolder_to_saving:
    #        visualiser.print_individuals(all_objectives, population_number, simulation_results_store,
    #                                     all_breakers_store, fitnesses=None, maxiters=maxiters)
    return all_objectives


def crossover(p1, p2, rate, genotype_mask):
    random_val = random.random()
    if random_val >= rate:
        return p1

    new_individ = Individual(copy.deepcopy(p1.genotype))

    is_bad = True
    iteration = 0

    genotype_encoder = StaticStorage.genotype_encoder

    while is_bad:
        print(f'CROSSOVER_{iteration}')

        new_breakers = genotype_encoder.mutate(p1.genotype, p2.genotype)

        constraints = StaticStorage.task.constraints

        is_bad = _validate_constraints(new_breakers, constraints)
        if not is_bad:
            new_individ.genotype = copy.copy(new_breakers)
        iteration += 1

    return new_individ


def mutation(individ, rate, mutation_value_rate, genotype_mask):
    new_individ = Individual(copy.deepcopy(individ.genotype))

    random_val = random.random()

    if random_val >= rate:
        genotype_encoder = StaticStorage.genotype_encoder
        iteration = 0
        is_bad = True

        while is_bad:
            print(f'MUTATION_{iteration}')

            new_breakers = genotype_encoder.mutate(new_individ.genotype)
            constraints = StaticStorage.task.constraints

            is_bad = _validate_constraints(new_breakers, constraints)

            if not is_bad:
                new_individ.genotype = copy.copy(new_breakers)
            iteration += 1
    return new_individ


def initial_pop_random(size, **kwargs):
    print("INITIAL")
    population_new = []

    genotype_encoder = StaticStorage.genotype_encoder
    for _ in range(0, size):

        while len(population_new) < size:
            genotype = np.zeros(StaticStorage.genotype_length)
            for j, g in enumerate(genotype):
                if j % 2 == 0:
                    genotype[j] = random.randint(genotype_encoder.min_for_init[0],
                                                 genotype_encoder.max_for_init[0])
                else:
                    genotype[j] = random.randint(genotype_encoder.min_for_init[1],
                                                 genotype_encoder.max_for_init[1])

            breakers_from_genotype = genotype_encoder.parameterized_genotype_to_breakers(
                genotype,
                StaticStorage.task,
                StaticStorage.exp_domain.model_grid)

            constraints = StaticStorage.task.constraints

            is_bad = _validate_constraints(breakers_from_genotype, constraints)

            if not is_bad:
                population_new.append(
                    Individual(breakers_from_genotype))

    return population_new


def _validate_constraints(proposed_breakers, constraints):
    objective_calculation_data = ObjectiveData(StaticStorage.model.domain, proposed_breakers,
                                               StaticStorage.model.domain.base_breakers,
                                               None,
                                               None)
    for constraint in constraints:
        objective = constraint[0]
        comparison_type = constraint[1]
        constr_value = constraint[2]

        if objective.is_simulation_required:
            raise NotImplementedError

        obj_val = objective.get_obj_value(objective_calculation_data)

        if comparison_type == ConstraintComparisonType.equal and not (obj_val == constr_value):
            is_bad = True
            break
        if comparison_type == ConstraintComparisonType.not_equal and not (obj_val != constr_value):
            is_bad = True
            break
    return is_bad
