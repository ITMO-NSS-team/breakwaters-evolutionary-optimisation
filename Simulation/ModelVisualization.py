import matplotlib.pyplot as plt
import numpy as np
import seaborn as sb
import os


class ModelsVisualization():

    def __init__(self, configuration_label, exp_name):
        self.configuration_label = configuration_label
        self.exp_name = exp_name

    def simple_visualise(self, hs: np.ndarray, all_breakers, base_breakers, fairways, target_points, fitness=None):

        plt.rcParams['figure.figsize'] = [15, 10]
        ax = plt.subplot()

        values = str(round(hs[target_points[0].y][target_points[0].x], 2))
        for i in range(1, len(target_points)):
            values += ', ' + str(round(hs[target_points[i].y][target_points[i].x], 2))
        if fitness is not None:
            fit_str = ",".join(
                [str(round(f)) if not isinstance(f, list) else ",".join([str(int(round(hs))) for hs in f]) for f in
                 fitness])
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
            ax = sb.heatmap(hs, mask=mask, vmax=6, vmin=0, cmap='RdYlBu')

        breaker_points = []
        for i in range(len(all_breakers)):
            for j in range(1, len(all_breakers[i].points)):
                p1, p2 = [all_breakers[i].points[j - 1].x, all_breakers[i].points[j].x], \
                         [all_breakers[i].points[j - 1].y, all_breakers[i].points[j].y]
                plt.plot(p1, p2, c='r', linewidth=4, marker='o')

                if [all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y] not in breaker_points:
                    breaker_points.append([all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y])
                    plt.annotate(
                        f'({all_breakers[i].points[j-1].x},{all_breakers[i].points[j-1].y})',
                        (all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y))

                if j == len(all_breakers[i].points) - 1:
                    if [all_breakers[i].points[j].x, all_breakers[i].points[j].y] not in breaker_points:
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
            plt.annotate(f'[№{point_ind},{point.x+2},{point.y+2}]', (point.x, point.y), color='black')

        # plt.figure(figsize=(4, 5))
        if not os.path.isdir(f'img/{self.exp_name}'):
            os.mkdir(f'img/{self.exp_name}')

        plt.savefig(f'img/{self.exp_name}/{self.configuration_label}.png')
        # plt.show()
        plt.clf()
