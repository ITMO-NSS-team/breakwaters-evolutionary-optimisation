import math
import os
import re
import warnings
import pygmo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from EvoAlgs.SPEA2.RawFitness import raw_fitness
from CommonUtils.StaticStorage import StaticStorage
from EvoAlgs.EvoAnalytics import EvoAnalytics
from Optimisation.Objective import CostObjective,RelativeCostObjective,RelativeNavigationObjective,RelativeQuailityObjective,RelativeWaveHeightObjective
from Visualisation.ModelVisualization import ModelsVisualization
from  Breakers.BreakersUtils import BreakersUtils
from EvoAlgs.SPEA2 import SPEA2

warnings.filterwarnings("ignore")


class VisualiserState:
    def __init__(self, generation_number):
        self.generation_number = generation_number


class VisualisationSettings:
    def __init__(self, store_all_individuals, store_best_individuals, num_of_best_individuals_from_population_for_print,
                 create_gif_image, create_boxplots, print_pareto_front=True,create_pareto_set_chart_during_optimization=None,create_boxplots_during_optimization=None):
        self.store_all_individuals = store_all_individuals
        self.store_best_individuals = store_best_individuals
        self.num_of_best_individuals = num_of_best_individuals_from_population_for_print
        self.create_gif_image = create_gif_image
        self.create_boxplots = create_boxplots
        self.print_pareto_front = print_pareto_front
        self.create_pareto_set_chart_during_optimization=create_pareto_set_chart_during_optimization
        self.create_boxplots_during_optimization=create_boxplots_during_optimization
        return


class VisualisationData:
    def __init__(self, optimisation_objectives, base_breakers, task, data_for_pareto_set_chart=None):
        self.optimisation_objectives = optimisation_objectives
        self.base_breakers = base_breakers
        self.task = task
        self.data_for_pareto_set_chart = data_for_pareto_set_chart
        self.labels=[[] for i in range(len(data_for_pareto_set_chart))]
        for chart_num,chart_data in enumerate(data_for_pareto_set_chart):
            for axis in range(len(chart_data)):
                if isinstance(data_for_pareto_set_chart[chart_num][axis],RelativeCostObjective):
                    self.labels[chart_num].append("cost")
                    self.labels[chart_num].append("Повышение цены")
                    continue
                if isinstance(data_for_pareto_set_chart[chart_num][axis],RelativeWaveHeightObjective):
                    self.labels[chart_num].append("hs")
                    self.labels[chart_num].append("Среднее снижение hs по всем точкам")
                    continue
                if isinstance(data_for_pareto_set_chart[chart_num][axis],RelativeNavigationObjective):
                    self.labels[chart_num].append("navigation")
                    self.labels[chart_num].append("Ухудшение/улучшение безопасности мореплавания")
                    continue

        return

class Visualiser:

    def __init__(self, visualisation_settings, visualisation_data):

        self.exp_name = EvoAnalytics.run_id
        self.state = VisualiserState(0)
        self.maxiters = None
        self.visualisation_settings = visualisation_settings
        self.visualisation_data = visualisation_data

    def print_pareto_set(self, best_individuals_indexes,population):

        directory = EvoAnalytics.run_id

        if not os.path.isdir("pareto_front"):
            os.mkdir("pareto_front")

        for chart_num,chart_data in enumerate(self.visualisation_data.labels):

            for i in range(0,len(chart_data),2):
                if i==0:
                    chart_name=chart_data[i]

                else:
                    chart_name=chart_name+'_and_'+chart_data[i]

            if not os.path.isdir(f'pareto_front/{chart_name}'):
                os.mkdir(f'pareto_front/{chart_name}')
            if not os.path.isdir(f'pareto_front/{chart_name}/{directory}'):
                os.mkdir(f'pareto_front/{chart_name}/{directory}')

            axis_data = [[] for axis in range(len(self.visualisation_data.data_for_pareto_set_chart[chart_num]))]
            for num_of_index, index_of_best_ind in enumerate(best_individuals_indexes):

                for axis_num,axis in enumerate(self.visualisation_data.data_for_pareto_set_chart[chart_num]):

                    if isinstance(axis, RelativeWaveHeightObjective):
                        axis_data[axis_num].append(math.fabs(np.mean([population[index_of_best_ind].objectives[objective_number] for objective_number in range(len(StaticStorage.task.objectives) - 1, len(population[index_of_best_ind].objectives))])))
                        continue
                    else:
                        for obj_num, obj in enumerate(StaticStorage.task.objectives[:len(StaticStorage.task.objectives)-1]):
                            if isinstance(axis, type(obj)):
                                axis_data[axis_num].append(math.fabs(population[index_of_best_ind].objectives[obj_num]))

            if len(self.visualisation_data.data_for_pareto_set_chart[chart_num])==2:
                EvoAnalytics.print_pareto_set_(data=axis_data,
                                                 save_directory=f'pareto_front/{chart_name}/{directory}/{self.state.generation_number+1}.png',
                                                 population_num=self.state.generation_number,labels=[self.visualisation_data.labels[chart_num][i] for i in range(1,len(self.visualisation_data.labels[chart_num]),2)])


    def print_pareto_set_from_history(self):
        #TO DO method to create patero set chart using history data from csv file
        pass

    def print_configuration(self, simulation_result, all_breakers, objective, dir, image_for_gif, num_of_population,
                            ind_num):

        visualiser = ModelsVisualization(str(num_of_population + 1) + "_" + str(ind_num + 1))

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(),
                                    all_breakers,
                                    self.visualisation_data.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    objective, dir=dir, image_for_gif=image_for_gif,
                                    population_and_ind_number=[num_of_population, ind_num])

        del visualiser

    def print_individuals(self, population, fitnesses=None, maxiters=None,):

        num_of_population = self.state.generation_number

        if self.visualisation_settings.store_best_individuals or self.visualisation_settings.print_pareto_front:
            if StaticStorage.multi_objective_optimization:
                if self.visualisation_data.task.goal == "minimize":
                    best_individuals_indexes = np.argsort(raw_fitness(population))
                    #pygmo.fast_non_dominated_sorting([ind.objectives for ind in population])
                else:
                    best_individuals_indexes = np.argsort(raw_fitness(population))[::-1]

            else:
                # TO DO
                # The case for  signgle-objective optimization
                pass


            for ind_num, ind_index in enumerate(best_individuals_indexes):
                self.print_configuration(simulation_result=population[ind_index].simulation_result, all_breakers=BreakersUtils.merge_breakers_with_modifications(self.visualisation_data.base_breakers,
                                                                           population[ind_index].genotype.get_genotype_as_breakers()),
                                         objective=population[ind_index].genotype.get_parameterized_chromosome_as_num_list(), dir="best_individuals", image_for_gif=True,
                                         num_of_population=self.state.generation_number, ind_num=ind_num)

        if self.visualisation_settings.store_all_individuals:

            for ind_num,individ in enumerate(population):
                self.print_configuration(simulation_result=individ.simulation_result, all_breakers=BreakersUtils.merge_breakers_with_modifications(self.visualisation_data.base_breakers,
                                                                           individ.genotype.get_genotype_as_breakers()), objective=individ.genotype.get_parameterized_chromosome_as_num_list(), dir="all_individuals", image_for_gif=False,
                                         num_of_population=self.state.generation_number, ind_num=ind_num)



        if self.visualisation_settings.create_pareto_set_chart_during_optimization:
            self.print_pareto_set(best_individuals_indexes,population)

        if self.visualisation_settings.create_boxplots_during_optimization:
            pass #TO DO

    def gif_image_maker(self, directory=EvoAnalytics.run_id, gif_type="breakers"):

        if gif_type == "pareto2D":
            for data_types in self.visualisation_data.data_for_pareto_set_chart:
                path = str(os.path.abspath(os.curdir)) + "\\pareto_front\\" + "img\\" + data_types[0] + "_to_" + \
                       data_types[1] + "\\" + directory + "\\"
                save_path = str(os.path.abspath(os.curdir)) + "\\gif_img\\" + directory + "\\"
                print("path", path)
                print("save path", save_path)
                images = []
                for i in range(self.maxiters):
                    images.append(Image.open(path + str(i) + ".png"))

                images[0].save("{}.gif".format(save_path + data_types[0] + "_to_" + data_types[1]), save_all=True,
                               append_images=images[1:], duration=300,
                               loop=0)

            return

        if not os.path.isdir(f'wave_gif_imgs/{directory}'):
            os.mkdir(f'wave_gif_imgs/{directory}')

        if gif_type == "breakers":
            path = "wave_gif_imgs/" + directory + "/"
        else:
            path = "boxplots/" + str(gif_type) + "/" + directory + "/"

        images = []
        sorted_names_of_images = []

        for i1 in range(self.maxiters):
            for i2 in range(self.visualisation_settings.num_of_best_individuals):
                sorted_names_of_images.append("{}_{}.png".format(i1 + 1, i2 + 1))

        for filename in sorted_names_of_images:
            images.append(Image.open(path + filename))

        save_path = str(os.path.abspath(os.curdir)) + "\\gif_img\\" + directory + "\\"

        if gif_type == "breakers":
            images[0].save("{}breakers.gif".format(save_path), save_all=True, append_images=images[1:], duration=100,
                           loop=0)
        else:
            images[0].save("{}{}.gif".format(save_path, gif_type), save_all=True, append_images=images[1:],
                           duration=100,
                           loop=0)

    def gif_images_maker(self, directory=None):

        if not os.path.isdir('gif_img'):
            os.mkdir('gif_img')

        if directory:
            run_id = directory
        else:
            run_id = EvoAnalytics.run_id

        if not os.path.isdir(f'gif_img/{run_id}'):
            os.mkdir(f'gif_img/{run_id}')

        self.gif_image_maker(run_id, gif_type="breakers")
        self.gif_image_maker(run_id, gif_type="gen_len")
        self.gif_image_maker(run_id, gif_type="obj")
        self.gif_image_maker(run_id, gif_type="pareto2D")

    def gif_series_maker(self, directory=None, gif_type="breakers"):

        if not os.path.isdir('series'):
            os.mkdir('series')

        if not directory:
            directory = EvoAnalytics.run_id

        if not os.path.isdir(f'series/{EvoAnalytics.run_id}'):
            os.mkdir(f'series/{EvoAnalytics.run_id}')

        num_of_subplots = 3

        for i1 in range(self.maxiters):

            for i2 in range(self.visualisation_settings.num_of_best_individuals):
                images = []
                # sorted_names_of_images.append("{}_{}.png".format(i1 + 1, i2 + 1))
                images.append(Image.open("wave_gif_imgs/" + directory + "/" + str(i1 + 1) + "_" + str(i2 + 1) + ".png"))
                images.append(Image.open(
                    "boxplots/" + "gen_len" + "/" + directory + "/" + str(i1 + 1) + "_" + str(i2 + 1) + ".png"))
                images.append(
                    Image.open("boxplots/" + "obj" + "/" + directory + "/" + str(i1 + 1) + "_" + str(i2 + 1) + ".png"))

                plt.rcParams['figure.figsize'] = [25, 15]

                f, axarr = plt.subplots(1, num_of_subplots)
                plt.subplots_adjust(wspace=0.1, hspace=0)

                for j in range(num_of_subplots):
                    axarr[j].set_yticklabels([])
                    axarr[j].set_xticklabels([])
                    axarr[j].imshow(images[j])

                plt.savefig("series/" + EvoAnalytics.run_id + "/" + str(i1 + 1) + "_" + str(i2 + 1) + ".png",
                            bbox_inches='tight')

        if not os.path.isdir(f'gif_img/{directory}'):
            os.mkdir(f'gif_img/{directory}')
        images = []
        for i1 in range(self.maxiters):
            for i2 in range(self.visualisation_settings.num_of_best_individuals):
                images.append(Image.open("series/{}/{}_{}.png".format(directory, i1 + 1, i2 + 1)))

        images[0].save("gif_img/{}/Graphs.gif".format(directory), save_all=True, append_images=images[1:], duration=100,
                       loop=0)

    # def print_pareto_front(self, objectives):
