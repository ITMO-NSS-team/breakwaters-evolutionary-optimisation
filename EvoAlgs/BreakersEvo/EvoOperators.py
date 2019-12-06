import copy
import itertools
import os
import random
import uuid
from itertools import chain
import copy

import numpy as np
import pandas as pd
from pyDOE import lhs
from scipy.stats.distributions import norm

from Breakers.BreakersUtils import BreakersUtils
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.BreakersEvo.BreakersEvoUtils import BreakersEvoUtils
from EvoAlgs.BreakersEvo.BreakerStructureRepresentation import BreakerStructureRepresentation
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import ObjectiveData, ConstraintComparisonType
from Visualisation.ModelVisualization import ModelsVisualization
from Simulation.Results import WaveSimulationResult

# TODO refactor
len_range = [0, 3]
dir_range = [-50, 50]


def _flatten(items, seqtypes=(list, tuple)):
    for i, x in enumerate(items):
        while i < len(items) and isinstance(items[i], seqtypes):
            items[i:i + 1] = items[i]
    return items


def calculate_objectives(model, task, population, visualiser=None):
    if any(obj.is_simulation_required for obj in task.objectives):
        pre_simulated_results = model.computational_manager.prepare_simulations_for_population(population, model) \
            if any(obj.is_simulation_required for obj in task.objectives) else None

    for individ_index, individual in enumerate(population):
        label_to_reference = None

        proposed_breakers = individual.genotype.get_genotype_as_breakers()
        objectives_values = []

        simulation_result = None
        base_simulation_result = None

        for obj_ind, obj in enumerate(task.objectives):
            if obj.is_simulation_required:
                base_simulation_result = pre_simulated_results[len(pre_simulated_results) - 1]
                simulation_result = pre_simulated_results[individ_index]

            objective_calculation_data = ObjectiveData(model.domain, proposed_breakers, model.domain.base_breakers,
                                                       simulation_result,
                                                       base_simulation_result)

            new_obj_value = obj.get_obj_value(objective_calculation_data)

            objectives_values.append(new_obj_value)

            if obj.is_simulation_required:
                try:
                    simulation_result = pre_simulated_results[individ_index]
                except:
                    print("Simulated result not found in pre-simulated results")

            else:
                if not any(obj.is_simulation_required for obj in task.objectives):
                    # stub for simulation results if no simulations needed
                    label = uuid.uuid4().hex
                    simulation_result = WaveSimulationResult(
                        hs=np.zeros(shape=(model.domain.model_grid.grid_y, model.domain.model_grid.grid_x)),
                        configuration_label=label)

        # un-list objectives
        objectives_values = _flatten(objectives_values)

        individual.objectives = objectives_values
        individual.simulation_result = simulation_result

        EvoAnalytics.save_cantidate(individual.population_number, individual.objectives, individual.genotype.get_parameterized_chromosome_as_num_list())

    if visualiser is not None:
        visualiser.print_individuals(population, fitnesses=None)
        #visualiser.print_individuals([individual.objectives], [individual.simulation_result],
                                         #[proposed_breakers], fitnesses=None)


def crossover(p1, p2, rate):
    random_val = random.random()
    if random_val >= rate:
        return p1

    new_individ = BreakerStructureRepresentation(copy.deepcopy(p1.genotype))

    is_bad = True
    iteration = 0

    genotype_encoder = StaticStorage.genotype_encoder

    while is_bad:
        print(f'CROSSOVER_{iteration}')

        new_breakers = genotype_encoder.onepoint_crossover(p1.genotype, p2.genotype)

        constraints = StaticStorage.task.constraints

        is_bad = _validate_constraints(new_breakers, constraints)
        if not is_bad:
            print("Accepted")
            new_individ.genotype = copy.deepcopy(new_breakers)
        iteration += 1

    return new_individ


def mutation(individ, rate, mutation_value_rate):
    new_individ = BreakerStructureRepresentation(copy.deepcopy(individ.genotype))

    random_val = random.random()

    if random_val < rate:
        genotype_encoder = StaticStorage.genotype_encoder
        iteration = 0
        is_bad = True

        while is_bad:
            print(f'MUTATION_{iteration}')

            new_breakers = genotype_encoder.mutate(new_individ.genotype)
            constraints = StaticStorage.task.constraints

            is_bad = _validate_constraints(new_breakers, constraints)

            if not is_bad:
                print("Accepted")
                new_individ.genotype = copy.deepcopy(new_breakers)

            iteration += 1
    return new_individ


def initial_pop_random(size, **kwargs):
    print("INITIAL")
    population_new = []

    genotype_encoder = StaticStorage.genotype_encoder
    for _ in range(0, size):

        while len(population_new) < size:

            new_breakers = genotype_encoder.space_fill(StaticStorage.task.possible_modifications)

            constraints = StaticStorage.task.constraints

            is_bad = _validate_constraints(new_breakers, constraints)

            if not is_bad:
                print("Accepted")
                population_new.append(
                    BreakerStructureRepresentation(new_breakers))

    return population_new


def _validate_constraints(proposed_breakers, constraints):
    objective_calculation_data = ObjectiveData(StaticStorage.exp_domain, proposed_breakers,
                                               StaticStorage.exp_domain.base_breakers,
                                               None,
                                               None)
    is_bad = False
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
