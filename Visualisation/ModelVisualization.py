import os
import matplotlib
import shutil

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import numpy as np
import seaborn as sb
from EvoAlgs.EvoAnalytics import EvoAnalytics
import math


class ModelsVisualization:

    def __init__(self, configuration_label, exp_name=None):
        self.configuration_label = configuration_label
        if not exp_name:
            self.exp_name = EvoAnalytics.run_id
        else:
            self.exp_name = exp_name

    def simple_visualise(self, hs: np.ndarray, all_breakers, base_breakers, fairways, target_points, fitness=None,
                         dir="img", image_for_gif=False, \
                         population_and_ind_number=[]):

        if not os.path.isdir(dir):
            os.mkdir(dir)

        # plt.axis('off')
        # plt.rcParams['xtick.labelsize'] = 10
        # plt.rcParams['ytick.labelsize'] = 0
        plt.rcParams['axes.titlesize'] = 20
        plt.rcParams['axes.labelsize'] = 20
        plt.rcParams['figure.figsize'] = [15, 10]
        plt.rcParams["font.size"] = "1" #точки

        # fig = plt.figure(figsize=(15, 10))
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
            sb.heatmap(hs, mask=mask, vmax=6, vmin=0, cmap='RdYlBu_r', cbar_kws={"shrink": 0.85,'ticks' : []}, xticklabels=False, yticklabels=False)

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
            # print(self.fairways[0].x1)

        for point_ind, point in enumerate(target_points):
            plt.scatter(point.x, point.y, color='black', marker='o')
            plt.annotate(f'[№{point_ind},{point.x + 2},{point.y + 2}]', (point.x, point.y), color='black')

        # plt.figure(figsize=(4, 5))
        if not os.path.isdir(f'{dir}/{self.exp_name}'):
            os.mkdir(f'{dir}/{self.exp_name}')

        plt.savefig(f'{dir}/{self.exp_name}/{self.configuration_label}.png', bbox_inches='tight')
        plt.cla()
        plt.clf()
        plt.close('all')

    def experimental_visualise(self, hs: np.ndarray, all_breakers, base_breakers, fairways, target_points,
                               title_mod, vmax, order_id, is_wind, rep_info, dir_info, real_ang, len_info):

        import warnings
        warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)

        plt.rcParams['figure.figsize'] = [7, 5]
        plt.rcParams["font.size"] = "8"
        fig = plt.figure(frameon=True)
        ax = plt.subplot()
        ax.axes.set_aspect('equal')

        # plt.axis('o')
        plt.tick_params(axis='both', left='off', top='off', right='off', bottom='off', labelleft='off', labeltop='off',
                        labelright='off', labelbottom='off')

        rect = patches.Rectangle((0, 0), hs.shape[1], hs.shape[0], linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(rect)

        for point_ind, point in enumerate(target_points):
            plt.scatter(point.x, point.y, color='orange', marker='o', zorder=10)

        values = str(round(hs[target_points[0].y][target_points[0].x], 2))
        for i in range(1, len(target_points)):
            values += ', ' + str(round(hs[target_points[i].y][target_points[i].x], 2))

        wind_str = "без учета локального ветра."
        if is_wind:
            wind_str = "с учетом локального ветра."

        ax.set_title(
            f'{order_id} Высоты волн с {title_mod}% обеспеченностью в целевых точках: {values} м. \n Направление волнения {dir_info} для повторяемости раз в  {rep_info} лет,\n {wind_str} Длины доп. сооружений:\n {len_info}')

        map_of_place = hs

        mask = np.zeros_like(map_of_place)
        for i in range(len(map_of_place)):
            for j in range(len(map_of_place[0])):
                if map_of_place[i][j] == -9.:
                    mask[i][j] = 1
                else:
                    mask[i][j] = 0

        with sb.axes_style("white"):
            ax = sb.heatmap(hs, mask=mask, vmax=vmax, vmin=0, cmap='RdYlBu_r', cbar_kws={"shrink": 0.85})

        # ax.set_aspect('auto')

        breaker_points = []
        for i in range(len(all_breakers)):
            for j in range(1, len(all_breakers[i].points)):
                p1, p2 = [all_breakers[i].points[j - 1].x, all_breakers[i].points[j].x], \
                         [all_breakers[i].points[j - 1].y, all_breakers[i].points[j].y]
                plt.plot(p1, p2, c='c', linewidth=4, marker='o')

                if [all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y] not in breaker_points:
                    breaker_points.append([all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y])
                    # plt.annotate(
                    #    f'({all_breakers[i].points[j-1].x},{all_breakers[i].points[j-1].y})',
                    #    (all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y))
                    plt.annotate(
                        f'({all_breakers[i].points[j-1].x},{all_breakers[i].points[j-1].y})',
                        (all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y))

                if j == len(all_breakers[i].points) - 1:
                    if [all_breakers[i].points[j].x, all_breakers[i].points[j].y] not in breaker_points:
                        breaker_points.append([all_breakers[i].points[j].x, all_breakers[i].points[j].y])
                        # plt.annotate(
                        #    f'({all_breakers[i].points[j].x},{all_breakers[i].points[j].y})',
                        #    (all_breakers[i].points[j].x, all_breakers[i].points[j].y))
                        plt.annotate(
                            f'({all_breakers[i].points[j].x},{all_breakers[i].points[j].y})',
                            (all_breakers[i].points[j].x, all_breakers[i].points[j].y))

        for i in range(len(base_breakers)):
            for j in range(1, len(base_breakers[i].points)):
                p1, p2 = [base_breakers[i].points[j - 1].x, base_breakers[i].points[j].x], \
                         [base_breakers[i].points[j - 1].y, base_breakers[i].points[j].y]
                plt.plot(p1, p2, c='black', linewidth=4, marker='o')

        for j in range(len(fairways)):
            p1, p2 = [fairways[j].x1, fairways[j].x2], [fairways[j].y1, fairways[j].y2]
            plt.plot(p1, p2, '--', c='g', linewidth=2, marker='.')
            # print(self.fairways[0].x1)

        #

        wind_names = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]

        base_x = 9
        base_y = 9
        k = 5
        for ang_ind, ang in enumerate([0, 45, 90, 135, 180, 225, 270, 315]):
            ang2 = (ang + 120) % 360
            new_x = np.sin(ang2 / 180 * math.pi) * k
            new_y = -np.cos(ang2 / 180 * math.pi) * k

            plt.plot([base_x, base_x + new_x], [base_y, base_x + new_y], color="black")

            new_x = np.sin(ang2 / 180 * math.pi) * (k + 2)
            new_y = -np.cos(ang2 / 180 * math.pi) * (k + 2)

            plt.annotate(wind_names[ang_ind], (base_x + new_x, base_y + new_y), color='black')

        real_ang = (real_ang + 120 + 180) % 360

        new_x = np.sin(real_ang / 180 * math.pi) * (k + 2)
        new_y = -np.cos(real_ang / 180 * math.pi) * (k + 2)

        plt.arrow(base_x, base_y, new_x, new_y, length_includes_head=True,
                  head_width=0.5, head_length=0.5, color="cyan", width=0.2, zorder=10)

        # plt.figure(figsize=(4, 5))
        if not os.path.isdir(f'img/experiments/{self.exp_name}'):
            os.mkdir(f'img/experiments/{self.exp_name}')
        plt.savefig(f'img/experiments/{self.exp_name}/{self.configuration_label}.png', bbox_inches='tight')
        # plt.show()
        plt.clf()

    # def visualise_individuals_to_storage(self):

    # def visualise_best_individuals(self):

    def make_directory_for_gif_images(self):
        if not os.path.isdir(f'wave_gif_imgs/{self.exp_name}'):
            os.mkdir(f'wave_gif_imgs/{self.exp_name}')

    def gif_images_saving(self, population_num, num_in_best_ind_set):

        dir = str(os.path.abspath(os.curdir)).replace('\\', '/')
        # dir = str(os.path.abspath(os.curdir))
        shutil.copy(dir + "/img/" + str(self.exp_name) + "/" + str(self.configuration_label) + ".png", \
                    dir + "/wave_gif_imgs/" + str(self.exp_name) + "/" + str(population_num + 1) + "_" + str(
                        num_in_best_ind_set + 1) + ".png")

        # image1=cv2.imwrite("wave_gif_imgs"+str(self.exp_name)+"/"+str(self)+str(population_num)+"_"+str(num_in_best_ind_set)+".png",image)
