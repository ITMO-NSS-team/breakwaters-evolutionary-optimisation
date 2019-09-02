import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import seaborn as sns
import re


class EvoAnalytics:
    run_id = "opt_0"

    @staticmethod
    def clear():
        hist_file_name = f'history_{EvoAnalytics.run_id}.csv'
        if os.path.isfile(hist_file_name):
            os.remove(hist_file_name)

    @staticmethod
    def save_cantidate(pop_num, objectives, genotype, referenced_dataset):
        hist_file_name = f'history_{EvoAnalytics.run_id}.csv'
        if not os.path.isfile(hist_file_name):
            with open(hist_file_name, 'w', newline='') as f:
                EvoAnalytics._write_header_to_csv(f, objectives, genotype, referenced_dataset)
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objectives, genotype, referenced_dataset)
        else:
            with open(hist_file_name, 'a', newline='') as f:
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objectives, genotype, referenced_dataset)

    @staticmethod
    def _write_candidate_to_csv(f, pop_num, objs, genotype, referenced_dataset):
        # Количество значений целевых функций
        # print("objs",objs)
        writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [pop_num, referenced_dataset, ','.join([str(round(_, 1)) for _ in objs]),
             ','.join([str(round(_, 1)) for _ in genotype])])

    @staticmethod
    def _write_header_to_csv(f, objectives, genotype, referenced_dataset):

        writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["pop_num", "referenced_dataset", ','.join([f'obj{_}' for _ in range(0, len(objectives))]),
             ','.join([f'gen_len_{int(_ / 2)}' if _ % 2 == 0 else f'gen_dir_{int(_ / 2)}' for _ in
                       range(0, len(genotype))])])

    @staticmethod
    #TODO move to file creation method
    def change_symbol_in_file(file=None, symbol=',', symbol_for_change=';'):
        if not file:
            file = f'history_{EvoAnalytics.run_id}.csv'
        with open(file, 'r+') as f:
            txt = f.read().replace(symbol_for_change, symbol)
            f.seek(0)
            f.truncate()
            f.write(txt)

    @staticmethod
    def chart_series_creator(f=None, chart_type='boxplot', data_for_analyze='gen_len'):  # gen_len,obj and so on

        if not f:
            f = f'history_{EvoAnalytics.run_id}.csv'

        EvoAnalytics.change_symbol_in_file(f)

        df = pd.read_csv(f, header=0)
        indexes_of_new_launches = df[df['pop_num'] == 'pop_num'].index  # Начала строк для разделений
        num_of_launches = len(indexes_of_new_launches) + 1

        # Разделение
        df_of_launch = [df[:indexes_of_new_launches[0]]]
        df_of_launch[0]['pop_num'] = pd.to_numeric(df_of_launch[0]['pop_num'])
        num_of_generations = df_of_launch[0]['pop_num'].max() + 1
        pop_size = int(indexes_of_new_launches[0] / num_of_generations)
        # pop_size=df[df['pop_num']=='0'].index #Количество индивидов в популяции
        df = df.drop(df[df['pop_num'] == 'pop_num'].index)  # Удаление строки идентичной заголовку
        df_of_launch += [df[num_of_generations * pop_size * i:num_of_generations * pop_size * (i + 1)] for i in
                         range(1, num_of_launches)]

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

        num_of_cols = 4
        num_of_rows = math.ceil(num_of_generations / num_of_cols)

        if chart_type == 'boxplot':

            for num_of_launch in range(len(df_of_launch)):
                fig, axs = plt.subplots(ncols=num_of_cols, nrows=num_of_rows)
                plt.rcParams['figure.figsize'] = (50, 40)
                # Размер хрифта подписей оси Х
                plt.rcParams['xtick.labelsize'] = 10
                # plt.rcParams['xtick.labelbottom']=True
                # Изменение расстояний между графиками
                # plt.subplots_adjust(wspace=0.5, hspace=0.2)
                gener = [[j, k] for j in range(num_of_rows) for k in range(num_of_cols)]

                axs[gener[0][0]][gener[0][0]].set_title("Population " + str(0))
                sns.boxplot(data=df_of_launch[num_of_launch][:30], palette="Blues", ax=axs[0][0], linewidth=2)
                for i in range(1, int(df_of_launch[0].shape[0] / pop_size)):
                    axs[gener[i][0]][gener[i][1]].set_title("Population " + str(i))
                    sns.boxplot(data=df_of_launch[num_of_launch][pop_size * i:pop_size * i + pop_size],
                                palette="Blues",
                                ax=axs[gener[i][0]][gener[i][1]], linewidth=2)
                plt.savefig(data_for_analyze + '_for_' + str(num_of_launch) + '_launch.png')
