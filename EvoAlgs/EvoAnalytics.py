import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
import math
import seaborn as sns
import re
import gc
from tkinter import messagebox
from CommonUtils.StaticStorage import StaticStorage


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
    def save_cantidate(pop_num, objectives, anlytics_objectives, genotype, referenced_dataset, local_id,
                       subfolder_name=None):

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
                EvoAnalytics._write_header_to_csv(f, objectives, anlytics_objectives, genotype)
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objectives, anlytics_objectives, genotype,
                                                     referenced_dataset, local_id)
        else:
            with open(hist_file_name, 'a', newline='') as f:
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objectives, anlytics_objectives, genotype,
                                                     referenced_dataset, local_id)

    @staticmethod
    def _write_candidate_to_csv(f, pop_num, objs, analytics_objectives, genotype, referenced_dataset, local_id):
        writer = csv.writer(f, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [pop_num, referenced_dataset, ','.join([str(round(_, 1)) for _ in objs]),
             ','.join([str(round(_, 1)) for _ in analytics_objectives]),
             ','.join([str(round(_, 1)) for _ in genotype]), local_id])

    @staticmethod
    def _write_header_to_csv(f, objectives, analytics_objectives, genotype):

        writer = csv.writer(f, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["pop_num", "referenced_dataset", ','.join([f'obj{_}' for _ in range(0, len(objectives))]),
             ','.join([f'ananlytics_ob{_}' for _ in range(0, len(analytics_objectives))]),
             ','.join([f'gen_len_{int(_ / 2)}' if _ % 2 == 0 else f'gen_dir_{int(_ / 2)}' for _ in
                       range(0, len(genotype))]), "local_id"])

    @staticmethod
    def print_pareto_set_(data, save_directory, population_num, labels):
        fig, ax = plt.subplots()
        ax.set_title("Популяция" + str(population_num + 1))

        if labels[0] == "Повышение цены":
            ax.invert_xaxis()
            plt.xlim(60, 0)
            plt.ylim(0, 100)
        elif labels[1] == "Повышение цены":
            ax.invert_yaxis()
            plt.xlim(0, 100)
            plt.ylim(60, 0)

        ax.set_xlabel(labels[0], fontsize=15)
        ax.set_ylabel(labels[1], fontsize=15)
        ax.scatter(data[0], data[1], linewidths=7, color='g')
        plt.tick_params(axis='both', labelsize=15)
        fig.set_figwidth(7)
        fig.set_figheight(7)
        plt.savefig(save_directory, bbox_inches='tight')

    @staticmethod
    def create_boxplot(num_of_generation=None, f=None, data_for_analyze='obj', analyze_only_last_generation=True,series=False,num_of_launches=None):


        EvoAnalytics.set_params()

        if not os.path.isdir("boxplots"):
            os.mkdir("boxplots")

        if not os.path.isdir(f'boxplots/{str(data_for_analyze)}'):
            os.mkdir(f'boxplots/{str(data_for_analyze)}')

        if not os.path.isdir(f'boxplots/{data_for_analyze}/{EvoAnalytics.run_id}'):
            os.mkdir(f'boxplots/{data_for_analyze}/{EvoAnalytics.run_id}')

        plt.close("all")

        if not f:
            f = f'HistoryFiles/history_{EvoAnalytics.run_id}.csv'
        else:
            f = f

        df = pd.read_csv(f, header=0)

        df = df.drop('referenced_dataset', 1)  # Removing the unnecessary column

        if analyze_only_last_generation: #else create image using History file
            df['pop_num'] = pd.to_numeric(df['pop_num'])
            num_of_generations = df['pop_num'].max()  # finding a last generation
            df = df.drop(
                df[df['pop_num'] != num_of_generations].index)  # Removing the rest lines

            df = df.reset_index(drop=True)  # Start the indexation in dataframe from 0

            num = 0
            for i in df.columns:
                if not re.search(data_for_analyze, i):
                    df.drop(i, axis=1, inplace=True)
                else:
                    if data_for_analyze == "gen_len":
                        df.rename(columns={i: 'L' + str(num)}, inplace=True)
                        num += 1

            for j in range(1, len(df.columns)):
                df[df.columns[j]] = pd.to_numeric(df[df.columns[j]])

            plt.close("all")

            ax = plt.subplot()
            plt.rcParams['axes.titlesize'] = 30
            f'Population {num_of_generation + 1}'
            ax.set_title(f'Population {num_of_generation + 1}')
            sns.boxplot(data=df, palette="Blues")

            plt.savefig(
                f'boxplots/{data_for_analyze}/{EvoAnalytics.run_id}/{num_of_generation + 1}.png')

            plt.close('all')

        else:
            if not num_of_launches:
                indexes_of_new_launches = df[df['pop_num'] == 'pop_num'].index

                num_of_launches = len(indexes_of_new_launches) + 1

            if num_of_launches > 1:
                df_of_launch = [df[:indexes_of_new_launches[0]]]
            else:
                df_of_launch = [df]

            df_of_launch[0]['pop_num'] = pd.to_numeric(df_of_launch[0]['pop_num'])

            num_of_generations = df_of_launch[0]['pop_num'].max() + 1

            if num_of_launches > 1:
                pop_size = int(indexes_of_new_launches[0] / num_of_generations)
                df = df.drop(df[df['pop_num'] == 'pop_num'].index)
                df_of_launch += [df[num_of_generations * pop_size * i:num_of_generations * pop_size * (i + 1)] for i in
                                 range(1, num_of_launches)]
            else:

                pop_size = len(df_of_launch[0].loc[df_of_launch[0]['pop_num'] == 0])

            for i in range(len(df_of_launch)):
                df_of_launch[i] = df_of_launch[i].reset_index(drop=True)
                for j in range(1, len(df.columns)):
                    df_of_launch[i][df.columns[j]] = pd.to_numeric(df_of_launch[i][df.columns[j]])

            for j in range(len(df_of_launch)):
                num = 0
                for i in df_of_launch[j].columns:
                    if not re.search(data_for_analyze, i):
                        df_of_launch[j].drop(i, axis=1, inplace=True)
                    else:
                        if data_for_analyze == "gen_len":
                            df_of_launch[j].rename(columns={i: 'L' + str(num)}, inplace=True)
                            num += 1

            plt.close("all")

            num_of_cols = 4
            num_of_rows = math.ceil(num_of_generations / num_of_cols)
            if series:
                plt.rcParams['figure.figsize'] = [40, 4 * num_of_rows]
            plt.rcParams['xtick.labelsize'] = 20
            plt.rcParams['ytick.labelsize'] = 20

            for num_of_launch in range(len(df_of_launch)):

                if series:

                    fig, axs = plt.subplots(ncols=num_of_cols, nrows=num_of_rows)
                    plt.subplots_adjust(hspace=.3)
                    gener = [[j, k] for j in range(num_of_rows) for k in range(num_of_cols)]

                    axs[gener[0][0]][gener[0][0]].set_title("Population 0")

                    sns.boxplot(data=df_of_launch[num_of_launch][:pop_size], palette="Blues", ax=axs[0][0],
                                linewidth=2)

                else:
                    EvoAnalytics.df_min_len = min([df_of_launch[0][i].min() for i in df_of_launch[0].columns])-2
                    EvoAnalytics.df_max_len = max([df_of_launch[0][i].max() for i in df_of_launch[0].columns])+2
                    plt.ylim(EvoAnalytics.df_min_len, EvoAnalytics.df_max_len)

                    ax = plt.subplot()

                    ax.set_title('Population 1')

                    sns.boxplot(data=df_of_launch[num_of_launch][:pop_size], palette="Blues")

                    plt.savefig(f'boxplots/{data_for_analyze}/{EvoAnalytics.run_id}/1.png')

                for i in range(1, int(df_of_launch[0].shape[0] / pop_size)):
                    if series:
                        axs[gener[i][0]][gener[i][1]].set_title(f'Population {i}')
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

                        plt.savefig(f'boxplots/{data_for_analyze}/{EvoAnalytics.run_id}/{i+1}.png')

                if series:
                    plt.savefig(f'{data_for_analyze}_for_launch-{EvoAnalytics.run_id}.png')
