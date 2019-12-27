import math
import os
import re
import glob
import seaborn as sb
import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from EvoAlgs.SPEA2.RawFitness import raw_fitness
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import CostObjective, RelativeCostObjective, RelativeNavigationObjective, \
    RelativeQuailityObjective, RelativeWaveHeightObjective, WaveHeightObjective
from Breakers.BreakersUtils import BreakersUtils

warnings.filterwarnings("ignore")


class VisualiserState:
    def __init__(self, generation_number):
        self.generation_number = generation_number


class VisualisationSettings:
    def __init__(self, store_all_individuals, store_best_individuals, num_of_best_individuals_from_population_for_print,
                 create_gif_image, create_boxplots, print_pareto_front=True,
                 create_pareto_set_chart_during_optimization=None, create_boxplots_during_optimization=None,
                 create_boxplots_from_history=None):
        self.store_all_individuals = store_all_individuals
        self.store_best_individuals = store_best_individuals
        self.num_of_best_individuals = num_of_best_individuals_from_population_for_print
        self.create_gif_image = create_gif_image
        self.create_boxplots = create_boxplots
        self.print_pareto_front = print_pareto_front
        self.create_pareto_set_chart_during_optimization = create_pareto_set_chart_during_optimization
        self.create_boxplots_during_optimization = create_boxplots_during_optimization
        self.create_boxplots_from_history = create_boxplots_from_history
        return


class VisualisationData:
    def __init__(self, optimisation_objectives, base_breakers, task, data_for_pareto_set_chart=None):
        self.optimisation_objectives = optimisation_objectives
        self.base_breakers = base_breakers
        self.task = task
        self.data_for_pareto_set_chart = data_for_pareto_set_chart
        self.labels = [[] for i in range(len(data_for_pareto_set_chart))]

        if data_for_pareto_set_chart:
            for chart_num, chart_data in enumerate(data_for_pareto_set_chart):
                for axis in range(len(chart_data)):
                    if data_for_pareto_set_chart[chart_num][axis].__class__.__name__ == 'RelativeCostObjective':
                        self.labels[chart_num].append("cost increase")
                        self.labels[chart_num].append("Повышение цены")
                        continue
                    if data_for_pareto_set_chart[chart_num][axis].__class__.__name__ == 'RelativeWaveHeightObjective':
                        self.labels[chart_num].append("hs")
                        self.labels[chart_num].append("Среднее снижение hs по всем точкам")
                        continue
                    if data_for_pareto_set_chart[chart_num][axis].__class__.__name__ == 'RelativeNavigationObjective':
                        self.labels[chart_num].append("navigation")
                        self.labels[chart_num].append("Ухудшение/улучшение безопасности мореплавания")
                        continue
                    if data_for_pareto_set_chart[chart_num][axis].__class__.__name__ == 'CostObjective':
                        self.labels[chart_num].append("cost")
                        self.labels[chart_num].append("Цена")
                        continue
                    #add others


        self.pareto_charts_folder_names = []
        for chart_num, chart_data in enumerate(self.labels):
            for i in range(0, len(self.labels[chart_num]), 2):
                if i == 0:
                    chart_name = chart_data[i]
                else:
                    chart_name = chart_name + '_and_' + chart_data[i]
            self.pareto_charts_folder_names.append(chart_name)

        return


class Visualiser:

    def __init__(self, visualisation_settings, visualisation_data):

        self.exp_name = EvoAnalytics.run_id
        self.state = VisualiserState(0)
        self.visualisation_settings = visualisation_settings
        self.visualisation_data = visualisation_data

    def print_pareto_set(self, best_individuals_indexes, population):
        if StaticStorage.is_verbose:
            print("labels", self.visualisation_data.labels)
        directory = EvoAnalytics.run_id

        if not os.path.isdir("pareto_front"):
            os.mkdir("pareto_front")

        n_points_to_opt = len(StaticStorage.task.mod_points_to_optimise) - 1
        for chart_num, chart_data in enumerate(self.visualisation_data.labels):

            if not os.path.isdir(f'pareto_front/{self.visualisation_data.pareto_charts_folder_names[chart_num]}'):
                os.mkdir(f'pareto_front/{self.visualisation_data.pareto_charts_folder_names[chart_num]}')
            if not os.path.isdir(
                    f'pareto_front/{self.visualisation_data.pareto_charts_folder_names[chart_num]}/{directory}'):
                print("FOLDER pareto chart name",self.visualisation_data.pareto_charts_folder_names[chart_num])
                os.mkdir(f'pareto_front/{self.visualisation_data.pareto_charts_folder_names[chart_num]}/{directory}')

            axis_data = [[] for axis in range(len(self.visualisation_data.data_for_pareto_set_chart[chart_num]))]

            for axis_num, axis in enumerate(self.visualisation_data.data_for_pareto_set_chart[chart_num]):

                for obj_num, obj in enumerate(StaticStorage.task.objectives + StaticStorage.task.analytics_objectives):
                    if axis.__class__.__name__ == obj.__class__.__name__:
                        num_of_wh_functions_before = 0
                        if obj_num != 0:
                            num_of_wh_functions_before = len([True for
                                                              objective_type in (
                                                                                            StaticStorage.task.objectives + StaticStorage.task.analytics_objectives)[
                                                                                :obj_num] if isinstance(objective_type,
                                                                                                        (
                                                                                                        WaveHeightObjective,
                                                                                                        RelativeWaveHeightObjective)) is True])

                        if axis.__class__.__name__ in ('WaveHeightObjective', 'RelativeWaveHeightObjective'):
                            for index_of_best_ind in best_individuals_indexes:
                                objective_values_of_ind = (population[index_of_best_ind].objectives + population[
                                    index_of_best_ind].analytics_objectives)

                                axis_data[axis_num].append(math.fabs(np.mean(
                                    [objective_values_of_ind[obj_value_num] for obj_value_num in
                                     range(obj_num + num_of_wh_functions_before * n_points_to_opt,
                                           obj_num + num_of_wh_functions_before * n_points_to_opt + n_points_to_opt)])))

                        else:
                            for index_of_best_ind in best_individuals_indexes:

                                objective_values_of_ind = (population[index_of_best_ind].objectives + population[
                                    index_of_best_ind].analytics_objectives)

                                axis_data[axis_num].append(math.fabs(objective_values_of_ind[
                                                                         obj_num + num_of_wh_functions_before * len(
                                                                             StaticStorage.mod_points_to_optimise)]))

            if len(self.visualisation_data.data_for_pareto_set_chart[chart_num]) == 2:
                EvoAnalytics.print_pareto_set_(data=axis_data,
                                               save_directory=f'pareto_front/{self.visualisation_data.pareto_charts_folder_names[chart_num]}/{directory}/{self.state.generation_number+1}.png',
                                               population_num=self.state.generation_number,
                                               labels=[self.visualisation_data.labels[chart_num][i] for i in
                                                       range(1, len(self.visualisation_data.labels[chart_num]), 2)])

            if StaticStorage.is_verbose:
                print("axis_data", axis_data)

    def print_configuration(self, simulation_result, all_breakers, objective, dir, image_for_gif, num_of_population,
                            ind_num, local_id):

        if not local_id:
            picture_name = f'{num_of_population+1}_{ind_num+1}'

        else:

            picture_name=f'{num_of_population+1}_{ind_num+1}(id{local_id})'

        self.simple_visualise(simulation_result.get_5percent_output_for_field(),
                                    all_breakers,
                                    self.visualisation_data.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    objective, dir=dir, image_for_gif=image_for_gif,
                                    population_and_ind_number=[num_of_population, ind_num],configuration_label=picture_name)


    def print_individuals(self, population):
        #try:
        if self.visualisation_settings.store_best_individuals or self.visualisation_settings.print_pareto_front:
            if StaticStorage.multi_objective_optimization:
                if self.visualisation_data.task.goal == "minimize":
                    best_individuals_indexes = np.argsort(raw_fitness(population))
                else:
                    best_individuals_indexes = np.argsort(raw_fitness(population))[::-1]

            else:
                if self.visualisation_data.task.goal == "minimize":
                    best_individuals_indexes=np.argsort([ind.objectives[0] for ind in population])[:self.visualisation_settings.num_of_best_individuals]
                else:
                    best_individuals_indexes = np.argsort([ind.objectives[0] for ind in population])[::-1][
                                               :self.visualisation_settings.num_of_best_individuals]

            for ind_num, ind_index in enumerate(best_individuals_indexes):
                self.print_configuration(simulation_result=population[ind_index].simulation_result,
                                         all_breakers=BreakersUtils.merge_breakers_with_modifications(
                                             self.visualisation_data.base_breakers,
                                             population[ind_index].genotype.get_genotype_as_breakers()),
                                         objective=population[
                                             ind_index].genotype.get_parameterized_chromosome_as_num_list(),
                                         dir="best_individuals", image_for_gif=True,
                                         num_of_population=self.state.generation_number, ind_num=ind_num,
                                         local_id=population[ind_index].local_id)

        if self.visualisation_settings.store_all_individuals:

            for ind_num, ind_index in enumerate(population):
                self.print_configuration(simulation_result=ind_index.simulation_result,
                                         all_breakers=BreakersUtils.merge_breakers_with_modifications(
                                             self.visualisation_data.base_breakers,
                                             ind_index.genotype.get_genotype_as_breakers()),
                                         objective=ind_index.genotype.get_parameterized_chromosome_as_num_list(),
                                         dir="all_individuals", image_for_gif=False,
                                         num_of_population=self.state.generation_number, ind_num=ind_num,
                                         local_id=None)

        if self.visualisation_settings.create_pareto_set_chart_during_optimization:
            self.print_pareto_set(best_individuals_indexes, population)

        if self.visualisation_settings.create_boxplots_during_optimization:

            f = f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
            for parameter in ('obj', 'gen_len'):
                EvoAnalytics.create_boxplot(num_of_generation=self.state.generation_number, f=f,
                                            data_for_analyze=parameter, analyze_only_last_generation=True)

        if self.state.generation_number == StaticStorage.max_gens - 1:
            if self.visualisation_settings.create_boxplots_from_history:
                for parameter in ('obj', 'gen_len'):
                    EvoAnalytics.create_boxplot(num_of_generation=self.state.generation_number, f=f,
                                                data_for_analyze=parameter, analyze_only_last_generation=False,series=True)


    def simple_visualise(self, hs: np.ndarray, all_breakers, base_breakers, fairways, target_points, fitness=None,
                         dir="img", image_for_gif=False, \
                         population_and_ind_number=[],configuration_label=None,exp_name=None):

        if not exp_name:
            exp_name=EvoAnalytics.run_id

        if not os.path.isdir(dir):
            os.mkdir(dir)

        plt.rcParams['axes.titlesize'] = 20
        plt.rcParams['axes.labelsize'] = 20
        plt.rcParams['figure.figsize'] = [15, 10]
        plt.rcParams["font.size"] = "1"  # точки

        ax = plt.subplot()
        plt.xticks([])
        plt.axis('off')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off',
                        labelright='off', labelbottom='off')
        ax.axes.set_aspect('equal')

        values = str(round(hs[target_points[0].y][target_points[0].x], 2))
        for i in range(1, len(target_points)):
            values += ', ' + str(round(hs[target_points[i].y][target_points[i].x], 2))
        if fitness is not None:
            fit_str = ",".join(
                [str(round(f)) if not isinstance(f, list) else ",".join([str(int(round(hs))) for hs in f]) for f in
                 fitness])

            if image_for_gif:

                ax.set_title(f'Generation {population_and_ind_number[0]+1}, \r\n'
                             f'Individ {population_and_ind_number[1]+1}')
            else:
                ax.set_title(f'Высоты волн с 5%-ной обеспеченносью в целевых точках: {values}, \r\n'
                             f'fitness {fit_str}')

        map_of_place = hs

        mask = np.zeros_like(map_of_place)
        for i in range(len(map_of_place)):
            for j in range(len(map_of_place[0])):
                if map_of_place[i][j] == -9.:
                    mask[i][j] = 1
                else:
                    mask[i][j] = 0

        with sb.axes_style("white"):
            sb.heatmap(hs, mask=mask, vmax=6, vmin=0, cmap='RdYlBu_r', cbar_kws={"shrink": 0.85, 'ticks': []},
                       xticklabels=False, yticklabels=False)

        breaker_points = []
        for i in range(len(all_breakers)):
            for j in range(1, len(all_breakers[i].points)):
                p1, p2 = [all_breakers[i].points[j - 1].x, all_breakers[i].points[j].x], \
                         [all_breakers[i].points[j - 1].y, all_breakers[i].points[j].y]
                plt.plot(p1, p2, c='r', linewidth=4, marker='o')

                if [all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y] not in breaker_points:
                    breaker_points.append([all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y])
                    plt.annotate(
                        f'({all_breakers[i].points[j - 1].x},{all_breakers[i].points[j - 1].y})',
                        (all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y))

                if j == len(all_breakers[i].points) - 1 and \
                        [all_breakers[i].points[j].x, all_breakers[i].points[j].y] not in breaker_points:
                    breaker_points.append([all_breakers[i].points[j].x, all_breakers[i].points[j].y])
                    plt.annotate(
                        f'({all_breakers[i].points[j].x},{all_breakers[i].points[j].y})',
                        (all_breakers[i].points[j].x, all_breakers[i].points[j].y))

        for i in range(len(base_breakers)):
            for j in range(1, len(base_breakers[i].points)):
                p1, p2 = [base_breakers[i].points[j - 1].x, base_breakers[i].points[j].x], \
                         [base_breakers[i].points[j - 1].y, base_breakers[i].points[j].y]
                plt.plot(p1, p2, c='c', linewidth=4, marker='o')

        for j in range(len(fairways)):
            p1, p2 = [fairways[j].x1, fairways[j].x2], [fairways[j].y1, fairways[j].y2]
            plt.plot(p1, p2, '--', c='g', linewidth=2, marker='.')

        for point_ind, point in enumerate(target_points):
            plt.scatter(point.x, point.y, color='black', marker='o')
            plt.annotate(f'[№{point_ind},{point.x + 2},{point.y + 2}]', (point.x, point.y), color='black')

        if not os.path.isdir(f'{dir}/{exp_name}'):
            os.mkdir(f'{dir}/{exp_name}')

        plt.savefig(f'{dir}/{exp_name}/{configuration_label}.png', bbox_inches='tight')
        plt.cla()
        plt.clf()
        plt.close('all')
