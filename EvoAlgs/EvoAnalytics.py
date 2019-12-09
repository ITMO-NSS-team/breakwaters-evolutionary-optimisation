import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import seaborn as sns
import re
import gc
import imageio
from tkinter import messagebox
from PIL import Image


class EvoAnalytics:
    plt.close("all")
    run_id = "opt_0"
    num_of_cols = 6
    num_of_generations = 0
    num_of_rows = math.ceil(num_of_generations / num_of_cols)
    num_of_best_inds_for_print = 5
    df_min_len = 0
    df_max_len = 1
    df_min_obj = 0
    df_max_obj = 1

    fig, axs = plt.subplots(ncols=num_of_cols, nrows=num_of_rows)
    pop_size = None
    gener = None
    plt.close("all")

    @staticmethod
    def set_params():
        gc.collect()
        plt.close("all")

        # plt.rcParams['figure.figsize'] = [40, 4 * EvoAnalytics.num_of_rows]
        # plt.rcParams['figure.figsize'] = [40, 40]
        plt.rcParams['xtick.labelsize'] = 30
        plt.rcParams['ytick.labelsize'] = 30
        plt.rcParams['axes.titlesize'] = 20
        plt.rcParams['axes.labelsize'] = 20

        EvoAnalytics.fig, EvoAnalytics.axs = plt.subplots(ncols=EvoAnalytics.num_of_cols,
                                                          nrows=EvoAnalytics.num_of_rows)
        plt.close("all")
        EvoAnalytics.gener = [[j, k] for j in range(EvoAnalytics.num_of_rows) for k in range(EvoAnalytics.num_of_cols)]

    @staticmethod
    def try_to_save_new_picture(data_for_analyze):
        plt.close("all")
        try:
            EvoAnalytics.fig.savefig(data_for_analyze + "_boxplots.png", bbox_inches='tight')
            return 1
        except:
            messagebox.showinfo("Error", "Please, close the file: " + data_for_analyze + "_boxplots.png")
            return 0

    @staticmethod
    def clear():
        hist_file_name = f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
        if os.path.isfile(hist_file_name):
            os.remove(hist_file_name)

    @staticmethod
    def save_cantidate(pop_num, objectives, genotype, referenced_dataset="None", subfolder_name=None):

        if not os.path.isdir(f'HistoryFiles'):
            os.mkdir(f'HistoryFiles')

        if subfolder_name:
            if not os.path.isdir(f'HistoryFiles/{subfolder_name}'):
                os.mkdir(f'HistoryFiles/{subfolder_name}')

            hist_file_name = f'HistoryFiles/{subfolder_name}/history_{EvoAnalytics.run_id}.csv'

        else:
            hist_file_name = f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
        if not os.path.isfile(hist_file_name):
            with open(hist_file_name, 'w', newline='') as f:
                EvoAnalytics._write_header_to_csv(f, objectives, genotype, referenced_dataset)
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objectives, genotype, referenced_dataset)
        else:
            with open(hist_file_name, 'a', newline='') as f:
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objectives, genotype, referenced_dataset)

        EvoAnalytics.change_symbol_in_file(file=hist_file_name)

    @staticmethod
    def _write_candidate_to_csv(f, pop_num, objs, genotype, referenced_dataset):
        # Количество значений целевых функций
        # print("objs",objs)
        writer = csv.writer(f, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [pop_num, referenced_dataset, ','.join([str(round(_, 1)) for _ in objs]),
             ','.join([str(round(_, 1)) for _ in genotype])])

    @staticmethod
    def _write_header_to_csv(f, objectives, genotype, referenced_dataset):

        writer = csv.writer(f, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["pop_num", "referenced_dataset", ','.join([f'obj{_}' for _ in range(0, len(objectives))]),
             ','.join([f'gen_len_{int(_ / 2)}' if _ % 2 == 0 else f'gen_dir_{int(_ / 2)}' for _ in
                       range(0, len(genotype))])])

    @staticmethod
    # TODO move to file creation method
    def change_symbol_in_file(file=None, symbol=',', symbol_for_change=';'):
        if not file:
            file = f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
        if os._exists(file):
            with open(file, 'w') as f:
                txt = f.write().replace(symbol_for_change, symbol)
                f.seek(0)
                f.truncate()
                f.write(txt)

    @staticmethod
    def print_pareto_set_(data, save_directory, population_num,labels):
        fig, ax = plt.subplots()
        ax.set_title("Популяция " + str(population_num + 1))

        if labels[0]=="Повышение цены":
            ax.invert_xaxis()
            plt.xlim(60, 0)
            plt.ylim(0, 100)
        elif labels[1]=="Повышение цены":
            ax.invert_yaxis()
            plt.xlim(0,100)
            plt.ylim(60, 0)

        if len(data)==2: #2D chart
            ax.set_xlabel(labels[0], fontsize=15)
            ax.set_ylabel(labels[1], fontsize=15)
            ax.scatter(data[0], data[1], linewidths=7, color='g')
            plt.tick_params(axis='both', labelsize=15)
            fig.set_figwidth(7)
            fig.set_figheight(7)
            plt.savefig(save_directory, bbox_inches='tight')
        else:
            pass # TO DO
        # the case with 3D

    @staticmethod
    def create_boxplot(num_of_generation=None, f=None, data_for_analyze='obj', analyze_only_last_generation=True,
                     chart_for_gif=False, first_generation=False, num_of_launches=1):

        if not os.path.isdir("boxplots"):
            os.mkdir("boxplots")

        if not os.path.isdir("boxplots/" + str(data_for_analyze)):
            os.mkdir("boxplots/" + str(data_for_analyze))

        plt.close("all")
        if not f:
            f = f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
        else:
            f = f
            # f = f'HistoryFiles/history_{f}.csv'

        EvoAnalytics.change_symbol_in_file(f)
        df = pd.read_csv(f, header=0)

        df = df.drop('referenced_dataset', 1)

        if analyze_only_last_generation:
            # Indexes_of_new_launches = df[df['pop_num'] == 'pop_num'].index  # Начала строк для разделений
            # num_of_launches = len(Indexes_of_new_launches) + 1
            # Разделение
            # if num_of_launches > 1:
            #    df = df[Indexes_of_new_launches[len(Indexes_of_new_launches) - 1] + 1:]
            df['pop_num'] = pd.to_numeric(df['pop_num'])

            num_of_generations = df['pop_num'].max()
            df = df.drop(
                df[df['pop_num'] != num_of_generations].index)  # Удаление строк не содержащих последнее поколение
            # Начать индексирование в dataframe с 0-ля

            df = df.reset_index(drop=True)

            num = 0
            for i in df.columns:
                if not re.search(data_for_analyze, i):
                    # df_of_launch[0]=df_of_launch[0].drop(df.columns[i], axis='columns')
                    df.drop(i, axis=1, inplace=True)
                else:
                    if data_for_analyze == "gen_len":
                        df.rename(columns={i: 'L' + str(num)}, inplace=True)
                        num += 1

            for j in range(1, len(df.columns)):
                df[df.columns[j]] = pd.to_numeric(df[df.columns[j]])

            if chart_for_gif:

                if not os.path.isdir("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id)):
                    os.mkdir("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id))

                plt.close("all")

                if first_generation == 0:
                    if data_for_analyze == "gen_len":

                        EvoAnalytics.df_min_len = min([df[i].min() for i in df.columns])
                        EvoAnalytics.df_max_len = max([df[i].max() for i in df.columns])

                    else:

                        EvoAnalytics.df_min_obj = min([df[i].min() for i in df.columns])
                        EvoAnalytics.df_max_obj = max([df[i].max() for i in df.columns])

                ax = plt.subplot()
                plt.rcParams['axes.titlesize']=30
                ax.set_title("Population " + str(num_of_generation + 1))

                '''
                if data_for_analyze == "gen_len":

                    # plt.ylim(EvoAnalytics.df_min_len, EvoAnalytics.df_max_len)
                    plt.ylim(0, 1.2)
                else:
                    plt.ylim(0, 400)
                '''

                sns.boxplot(data=df, palette="Blues")

                for i in range(EvoAnalytics.num_of_best_inds_for_print):
                    plt.savefig("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id) + "/" + str(
                        num_of_generation + 1) + "_" + str(i + 1) + ".png")

                plt.close('all')

            else:

                if not os.path.isdir("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id)):
                    os.mkdir("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id))

                EvoAnalytics.axs[EvoAnalytics.gener[num_of_generation][0]][
                    EvoAnalytics.gener[num_of_generation][1]].set_title("Population " + str(num_of_generation))
                sns.boxplot(data=df, palette="Blues", ax=EvoAnalytics.axs[EvoAnalytics.gener[num_of_generation][0]][
                    EvoAnalytics.gener[num_of_generation][1]], linewidth=2)
                plt.close('all')

                # EvoAnalytics.fig.savefig(data_for_analyze + "_boxplots.png",bbox_inches='tight')

                saving_process_is_completed = 0
                while saving_process_is_completed < 1:
                    saving_process_is_completed = EvoAnalytics.try_to_save_new_picture(data_for_analyze)

                gc.collect()
                plt.cla()
                plt.clf()
                plt.close('all')


        else:

            if not num_of_launches:
                indexes_of_new_launches = df[df['pop_num'] == 'pop_num'].index  # Начала строк для разделений

                num_of_launches = len(indexes_of_new_launches) + 1

            print("num_of_launches", df.index.stop)

            # Разделение
            if num_of_launches > 1:
                df_of_launch = [df[:indexes_of_new_launches[0]]]
            else:
                df_of_launch = [df]

            df_of_launch[0]['pop_num'] = pd.to_numeric(df_of_launch[0]['pop_num'])

            num_of_generations = df_of_launch[0]['pop_num'].max() + 1

            if num_of_launches > 1:
                pop_size = int(indexes_of_new_launches[0] / num_of_generations)
                df = df.drop(df[df['pop_num'] == 'pop_num'].index)  # Удаление строки идентичной заголовку
                df_of_launch += [df[num_of_generations * pop_size * i:num_of_generations * pop_size * (i + 1)] for i in
                                 range(1, num_of_launches)]
            else:

                pop_size = len(df_of_launch[0].loc[df_of_launch[0]['pop_num'] == 0])
                # pop_size=df_of_launch[df_of_launch['pop_num']==0].index #Количество индивидов в популяции

            # Начать индексирование в dataframe с 0-ля
            for i in range(len(df_of_launch)):
                df_of_launch[i] = df_of_launch[i].reset_index(drop=True)
                for j in range(1, len(df.columns)):
                    df_of_launch[i][df.columns[j]] = pd.to_numeric(df_of_launch[i][df.columns[j]])

            for j in range(len(df_of_launch)):
                num = 0
                for i in df_of_launch[j].columns:
                    if not re.search(data_for_analyze, i):
                        # df_of_launch[0]=df_of_launch[0].drop(df.columns[i], axis='columns')
                        df_of_launch[j].drop(i, axis=1, inplace=True)
                    else:
                        if data_for_analyze == "gen_len":
                            df_of_launch[j].rename(columns={i: 'L' + str(num)}, inplace=True)
                            num += 1

            plt.close("all")

            if not chart_for_gif:
                num_of_cols = 4
                num_of_rows = math.ceil(num_of_generations / num_of_cols)

                plt.rcParams['figure.figsize'] = [40, 4 * num_of_rows]
                # plt.rcParams['figure.figsize'] = [40, 40]
                plt.rcParams['xtick.labelsize'] = 15
                plt.rcParams['ytick.labelsize'] = 15

            for num_of_launch in range(len(df_of_launch)):

                if not chart_for_gif:
                    fig, axs = plt.subplots(ncols=num_of_cols, nrows=num_of_rows)

                    gener = [[j, k] for j in range(num_of_rows) for k in range(num_of_cols)]

                    axs[gener[0][0]][gener[0][0]].set_title("Population " + str(0))

                    sns.boxplot(data=df_of_launch[num_of_launch][:pop_size], palette="Blues", ax=axs[0][0],
                                linewidth=2)

                else:
                    if not os.path.isdir("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id)):
                        os.mkdir("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id))

                    EvoAnalytics.df_min_len = min([df_of_launch[0][i].min() for i in df_of_launch[0].columns])
                    EvoAnalytics.df_max_len = max([df_of_launch[0][i].max() for i in df_of_launch[0].columns])

                    # print("min and max", EvoAnalytics.df_min_len, "and", EvoAnalytics.df_max_len)
                    plt.ylim(EvoAnalytics.df_min_len, EvoAnalytics.df_max_len)

                    ax = plt.subplot()

                    ax.set_title("Population " + str(1))

                    sns.boxplot(data=df_of_launch[num_of_launch][:pop_size], palette="Blues")

                    for j in range(EvoAnalytics.num_of_best_inds_for_print):
                        plt.savefig(
                            "boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id) + "/" + "1_" + str(
                                j + 1) + ".png")

                    # for i in range(EvoAnalytics.num_of_best_inds_for_print):
                    # plt.savefig(
                    # "boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id) + "/" + str(
                    # num_of_generation + 1) + "_" + str(i + 1) + ".png")

                for i in range(1, int(df_of_launch[0].shape[0] / pop_size)):
                    if not chart_for_gif:
                        axs[gener[i][0]][gener[i][1]].set_title("Population " + str(i))
                        sns.boxplot(data=df_of_launch[num_of_launch][pop_size * i:pop_size * i + pop_size],
                                    palette="Blues",
                                    ax=axs[gener[i][0]][gener[i][1]], linewidth=2)

                    else:
                        plt.close("all")
                        fig = plt.figure()
                        ax = plt.subplot()
                        ax.set_title("Population " + str(i + 1))
                        plt.ylim(EvoAnalytics.df_min_len, EvoAnalytics.df_max_len)
                        sns.boxplot(data=df_of_launch[num_of_launch][pop_size * i:pop_size * i + pop_size],
                                    palette="Blues")
                        for j in range(EvoAnalytics.num_of_best_inds_for_print):
                            plt.savefig(
                                "boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id) + "/" + str(
                                    i + 1) + "_" + str(j + 1) + ".png")

                if not chart_for_gif:
                    plt.savefig(data_for_analyze + '_for_' + str(num_of_launch) + '_launch.png')

                # else:
                # for j in range(EvoAnalytics.num_of_best_inds_for_print):
                # plt.savefig("boxplots/" + str(data_for_analyze) + "/" + str(EvoAnalytics.run_id) + "/" + str(i + 1) + "_" + str(j + 1) + ".png")

                # plt.close('all')
