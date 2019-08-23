import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sb

class ModelsVisualization():

    def __init__(self, configuration_label):
        self.configuration_label = configuration_label

    def simple_visualise(self, hs: np.ndarray, all_breakers, fairways,target_points):

        plt.rcParams['figure.figsize'] = [15, 10]
        ax = plt.subplot()

        values = str(round(hs[target_points[0].y][target_points[0].x], 2))
        for i in range(1, len(target_points)):
            values += ', ' + str(round(hs[target_points[i].y][target_points[i].x], 2))

        ax.set_title('Высота волны в целевых точках: ' + values)

        map_of_place = np.loadtxt('map.txt')

        mask = np.zeros_like(map_of_place)
        for i in range(len(map_of_place)):
            for j in range(len(map_of_place[0])):
                if map_of_place[i][j] == -9.:
                    mask[i][j] = 1
                else:
                    mask[i][j] = 0

        with sb.axes_style("white"):
            ax = sb.heatmap(hs, mask=mask,cmap='RdYlBu')

        breaker_points = []
        for i in range(len(all_breakers)):
            for j in range(1, len(all_breakers[i].points)):
                p1, p2 = [all_breakers[i].points[j - 1].x, all_breakers[i].points[j].x], \
                         [all_breakers[i].points[j - 1].y, all_breakers[i].points[j].y]
                plt.plot(p1, p2, c='r', linewidth=3, marker='.')

                if [all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y] not in breaker_points:
                    breaker_points.append([all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y])
                    plt.annotate(
                        "(" + str(all_breakers[i].points[j - 1].x) + "," + str(all_breakers[i].points[j - 1].y) + ")", \
                        (all_breakers[i].points[j - 1].x, all_breakers[i].points[j - 1].y))

                if j == len(all_breakers[i].points) - 1:
                    if [all_breakers[i].points[j].x, all_breakers[i].points[j].y] not in breaker_points:
                        breaker_points.append([all_breakers[i].points[j].x, all_breakers[i].points[j].y])
                        plt.annotate(
                            "(" + str(all_breakers[i].points[j].x) + "," + str(all_breakers[i].points[j].y) + ")", \
                            (all_breakers[i].points[j].x, all_breakers[i].points[j].y))

        for j in range(len(fairways)):
            p1, p2 = [fairways[j].x1, fairways[j].x2], [fairways[j].y1, fairways[j].y2]
            plt.plot(p1, p2, c='g', linewidth=2, marker='.')
            # print(self.fairways[0].x1)

        # plt.figure(figsize=(4, 5))
        plt.savefig(f'img/{self.configuration_label}.png')
        #plt.show()
        plt.clf()
