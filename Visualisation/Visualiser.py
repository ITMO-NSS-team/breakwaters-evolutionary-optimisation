
from  EvoAlgs.EvoAnalytics import EvoAnalytics
from Visualisation.ModelVisualization import ModelsVisualization
from CommonUtils.StaticStorage import StaticStorage
from Optimisation.Objective import CostObjective, NavigationObjective, WaveHeightObjective, StructuralObjective, RelativeQuailityObjective
import math
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
import re

class Visualiser:

    def __init__(self,store_all_individuals,store_best_individuals,num_of_best_individuals_from_population_for_print,create_gif_image,create_boxplots,model,task,print_pareto_front=True,data_for_pareto_set_chart=None):

        self.exp_name = EvoAnalytics.run_id
        self.store_all_individuals=store_all_individuals
        self.store_best_individuals=store_best_individuals
        self.num_of_best_individuals=num_of_best_individuals_from_population_for_print
        self.create_gif_image=create_gif_image
        self.create_boxplots=True
        self.task=task
        self.model=model
        self.maxiters=None
        self.create_boxplots=create_boxplots
        self.print_pareto_front=print_pareto_front
        self.data_for_pareto_set_chart=data_for_pareto_set_chart


    def pareto_set_2D(self,x_axis=None, y_axis=None,file=None, directory=None):

        if not file:
            file = f'HistoryFiles/pareto_set/history_{EvoAnalytics.run_id}.csv'
        else:
            file = file

        if not directory:
            directory=EvoAnalytics.run_id

        if not os.path.isdir("pareto_front"):
            os.mkdir("pareto_front")
        if not os.path.isdir(f'pareto_front/img'):
            os.mkdir(f'pareto_front/img')
        if not os.path.isdir(f'pareto_front/img/{str(x_axis)}_to_{str(y_axis)}'):
            os.mkdir(f'pareto_front/img/{str(x_axis)}_to_{str(y_axis)}')
        if not os.path.isdir(f'pareto_front/img/{str(x_axis)}_to_{str(y_axis)}/{directory}'):
            os.mkdir(f'pareto_front/img/{str(x_axis)}_to_{str(y_axis)}/{directory}')

        EvoAnalytics.change_symbol_in_file(file)
        df = pd.read_csv(file, header=0)
        df['pop_num'] = pd.to_numeric(df['pop_num'])
        min_max_x_y = [[], []]
        columns_x_y=[]
        for j in range(self.maxiters):
            data = [[], []]
            indexes = df[df['pop_num'] == j].index

            for i,axis in enumerate((x_axis,y_axis)):

                if j==0:
                    if axis == "hs average decrease" or axis == "cost":  # and other characteristics related with objectives
                        columns = [i for i in df.columns if re.search('obj', i)]
                if axis == "hs average decrease":
                    if j==0:
                        columns_x_y.append(columns[len(self.task.objectives) - 1:])
                        for col in columns:
                            df[col] = pd.to_numeric(df[col])

                        data1=[]
                        for k in range(len(df)):
                            data1.append(np.mean(sum([df[col][k] for col in columns_x_y[i]])) * (-1))

                        min_max_x_y[i].append(min(data1))
                        min_max_x_y[i].append(max(data1))

                    for k in indexes:
                        data[i].append(np.mean(sum([df[col][k] for col in columns_x_y[i]]))*(-1))

                elif axis=="cost": #or some other char-s
                    if j==0:
                        for obj_num,obj in enumerate(self.task.objectives):
                            if isinstance(obj,CostObjective):
                                df["obj"+str(obj_num)] = pd.to_numeric(df["obj"+str(obj_num)])
                                min_max_x_y[i].append(df["obj"+str(obj_num)].min())
                                min_max_x_y[i].append(df["obj"+str(obj_num)].max())
                                columns_x_y.append(["obj"+str(obj_num)])
                                break
                    for k in indexes:
                        data[i].append(df[columns_x_y[i][0]][k])

            # create chart
            EvoAnalytics.print_pareto_set_2D(data=data,save_directory=f'pareto_front/img/{str(x_axis)}_to_{str(y_axis)}/{directory}/{j}.png',population_num=j, types_of_data=[x_axis, y_axis],min_max_x_y=min_max_x_y)
                    #df = df.drop(df[df['pop_num'] != num_of_generations].index)  # Удаление строк не содержащих последнее поколение


    def print_pareto_set_2D(self,objectives,num_of_population):
        mean_hs=[]
        cost_values=[]
        for objective in objectives:
            mean_hs.append(np.mean(objective[3:])*(-1))
            cost_values.append(objective[1])

        StaticStorage.mean_hhs.append(mean_hs)
        StaticStorage.costs.append(cost_values)

        '''
        fig, ax = plt.subplots()
        ax.set_title("Популяция " + str(num_of_population+1))
        ax.set_xlabel("Среднее снижение hs по всем точкам", fontsize=15)
        ax.set_ylabel("Цена", fontsize=15)
        ax.scatter(mean_hs, cost_values, linewidths=7,color='g')
        plt.tick_params(axis='both', labelsize=15)
        fig.set_figwidth(7)
        fig.set_figheight(7)
        '''
        '''
        ax = plt.subplot()
        plt.figure(figsize=(10, 10))
        ax.set_title("Population " + str(1))

        ax.set_xlabel("Среднее hs по всем точкам", fontsize=15)
        ax.set_ylabel("Цена", fontsize=15)

        plt.scatter(mean_hs, cost_values, linewidths=7)
        '''
        directory = EvoAnalytics.run_id

        if not os.path.isdir("pareto_front"):
            os.mkdir("pareto_front")
        if not os.path.isdir(f'pareto_front/img'):
            os.mkdir(f'pareto_front/img')
        if not os.path.isdir(f'pareto_front/gif'):
            os.mkdir(f'pareto_front/gif')
        if not os.path.isdir(f'pareto_front/img/{directory}'):
            os.mkdir(f'pareto_front/img/{directory}')
        if not os.path.isdir(f'pareto_front/gif/{directory}'):
            os.mkdir(f'pareto_front/gif/{directory}')

        #plt.savefig(f'pareto_front/img/{directory}/{num_of_population}.png', bbox_inches='tight')

    def print_configuration(self, simulation_result,all_breakers,objective,dir,image_for_gif,num_of_population,ind_num):

        print("population_number", num_of_population)
        print("ind num", ind_num)

        visualiser = ModelsVisualization(str(num_of_population + 1) + "_" + str(ind_num + 1))

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(),
                                    all_breakers,
                                    self.model.domain.base_breakers,
                                    StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                    objective,dir=dir, image_for_gif=image_for_gif,
                                    population_and_ind_number=[num_of_population, ind_num])

        del visualiser



    def print_individuals(self,objectives,num_of_population,simulation_result_store,all_breakers_store,fitnesses=None,maxiters=None):

        '''
        if StaticStorage.multi_objective_optimization:
            if self.print_pareto_front:
                for i in range(len(self.data_pareto)):
                    self.data_pareto[i].append()
        '''

        if num_of_population==0:
            self.maxiters = maxiters

        if self.store_best_individuals:
            if StaticStorage.multi_objective_optimization:
                #mean_fit=[np.mean(objective) for objective in objectives]
                mean_fit=[0.8 * objective[0] + 0.9 * objective[1] + 0.5 * objective[2] + sum(objective[3:]) for objective in objectives]
            else:
                mean_fit=fitnesses

            if self.task.goal=="minimization":
                best_for_print=np.argsort(mean_fit)[:self.num_of_best_individuals]
            else:
                best_for_print=np.argsort(mean_fit)[::-1][:self.num_of_best_individuals]
                #best_for_print = [i.genotype.genotype_array for i in sorted(enumerate(obj.ectives), key=lambda fit: np.mean(fit[1]) )[:EvoAnalytics.num_of_best_inds_for_print]]


        if self.store_all_individuals:
            image_for_gif=False
            dir="img"
            for ind_num in range(0,len(simulation_result_store)):

                self.print_configuration(simulation_result_store[ind_num],all_breakers_store[ind_num],objectives[ind_num],dir="img",image_for_gif=False,num_of_population=num_of_population,ind_num=ind_num)


        if self.store_best_individuals:

            for i,ind_num in enumerate(best_for_print):
                self.print_configuration(simulation_result_store[ind_num], all_breakers_store[ind_num], objectives[ind_num], dir="wave_gif_imgs", image_for_gif=True, num_of_population=num_of_population, ind_num=i)


        print("num of population",num_of_population+1)
        if num_of_population+1==maxiters:

            if self.print_pareto_front:
                for i in self.data_for_pareto_set_chart:
                    self.pareto_set_2D(x_axis=i[0],y_axis=i[1],file= f'HistoryFiles/pareto_set/history_{EvoAnalytics.run_id}.csv')

            if self.create_boxplots:

                EvoAnalytics.num_of_rows = math.ceil(EvoAnalytics.num_of_generations / EvoAnalytics.num_of_cols)
                EvoAnalytics.pop_size =len(objectives)
                EvoAnalytics.set_params()
                print("EvoAnalytics.num_of_generations",EvoAnalytics.num_of_generations)
                print("EvoAnalytics.num_of_cols",EvoAnalytics.num_of_cols)
                print("num_of_rows", EvoAnalytics.num_of_rows)
                print("pop_size", EvoAnalytics.pop_size)

                if StaticStorage.multi_objective_optimization:
                    f=f'HistoryFiles/pareto_set/history_{EvoAnalytics.run_id}.csv'
                else:
                    f=f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
                EvoAnalytics.create_chart(f=f,data_for_analyze='obj', analyze_only_last_generation=False, chart_for_gif=True)
                EvoAnalytics.create_chart(f=f,data_for_analyze='gen_len', analyze_only_last_generation=False,chart_for_gif=True)

            if self.create_gif_image:
                self.maxiters=maxiters
                self.gif_images_maker()
                self.gif_series_maker()

    def print_individ(self,objective,num_of_population,ind_num, simulation_result,all_breakers):
        image_for_gif=False
        dir="img"

        visualiser = ModelsVisualization(str(num_of_population + 1) + "_" + str(ind_num + 1))

        visualiser.simple_visualise(simulation_result.get_5percent_output_for_field(), all_breakers,
                                                self.model.domain.base_breakers,
                                                StaticStorage.exp_domain.fairways, StaticStorage.exp_domain.target_points,
                                                objective, dir=dir, image_for_gif=image_for_gif,
                                                population_and_ind_number=[num_of_population, ind_num])

    def gif_image_maker(self,directory=EvoAnalytics.run_id, gif_type="breakers"):

        if gif_type=="pareto2D":
            for data_types in self.data_for_pareto_set_chart:
                path=str(os.path.abspath(os.curdir)) + "\\pareto_front\\"+"img\\" +data_types[0]+"_to_"+data_types[1]+ directory + "\\"
                save_path = str(os.path.abspath(os.curdir)) + "\\gif_img\\" + directory + "\\"
                print("path",path)
                print("save path",save_path)
                images=[]
                for i in range (self.maxiters):
                    images.append(Image.open(path + str(i)+".png"))

                images[0].save("{}.gif".format(save_path+data_types[0]+"_to_"+data_types[1]), save_all=True, append_images=images[1:], duration=100,
                               loop=0)

            return

        if not os.path.isdir(f'wave_gif_imgs/{directory}'):
            os.mkdir(f'wave_gif_imgs/{directory}')

        if gif_type == "breakers":
            path = "wave_gif_imgs/" + directory + "/"
            # path = "C:\\Users\\YanaPolonskaya\\PycharmProjects\\breakwater-evo-opt (22.08.19 21 00)\\OptRuns\\wave_gif_imgs\\run_2019_10_03_17_24_59\\"
        else:
            path = "boxplots/" + str(gif_type) + "/" + directory + "/"
        # path="wave_gif_imgs/run_2019_09_28_01_40_10"

        # print("os.listdir(path)",sorted(os.listdir(path)))

        images = []
        sorted_names_of_images = []

        for i1 in range(self.maxiters):
            for i2 in range(self.num_of_best_individuals):
                sorted_names_of_images.append("{}_{}.png".format(i1 + 1, i2 + 1))

        for filename in sorted_names_of_images:
            images.append(Image.open(path + filename))

        # sorted_names_of_images=[str(j)+".png" for j in sorted([int(i.replace(".png","")) for i in os.listdir(path)])]

        save_path = str(os.path.abspath(os.curdir)) + "\\gif_img\\" + directory + "\\"

        if gif_type == "breakers":
            images[0].save("{}breakers.gif".format(save_path), save_all=True, append_images=images[1:], duration=100,
                           loop=0)
        else:
            images[0].save("{}{}.gif".format(save_path, gif_type), save_all=True, append_images=images[1:],
                           duration=100,
                           loop=0)

    def gif_images_maker(self,directory=None):



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
        self.gif_image_maker(run_id,gif_type="pareto2D")

    def gif_series_maker(self,directory=None, gif_type="breakers"):

        if not os.path.isdir('series'):
            os.mkdir('series')

        if not directory:
            directory = EvoAnalytics.run_id


        if not os.path.isdir(f'series/{EvoAnalytics.run_id}'):
            os.mkdir(f'series/{EvoAnalytics.run_id}')

        num_of_subplots = 3

        for i1 in range(self.maxiters):

            for i2 in range(self.num_of_best_individuals):
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
            for i2 in range(self.num_of_best_individuals):
                images.append(Image.open("series/{}/{}_{}.png".format(directory, i1 + 1, i2 + 1)))

        images[0].save("gif_img/{}/Graphs.gif".format(directory), save_all=True, append_images=images[1:], duration=100,
                       loop=0)

    #def print_pareto_front(self, objectives):