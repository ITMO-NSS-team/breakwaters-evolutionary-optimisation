import matplotlib.pyplot as plt
import numpy as np


class ModelsVisualization():

    def __init__(self,configuration_label):
        self.configuration_label=configuration_label


    def SimpleModelVisualization(self,hs: np.ndarray,base_breakers,fairways):
        plt.rcParams['figure.figsize'] = [20, 15]
        plt.imshow(hs, cmap='viridis')
        plt.colorbar()

        breaker_points=[]
        for i in range(len(base_breakers)):
            for j in range(1, len(base_breakers[i].points)):
                p1, p2 = [base_breakers[i].points[j - 1].x, base_breakers[i].points[j].x], \
                         [base_breakers[i].points[j - 1].y, base_breakers[i].points[j].y]
                plt.plot(p1, p2, c='r', linewidth=3, marker='.')


                if [base_breakers[i].points[j - 1].x, base_breakers[i].points[j - 1].y] not in breaker_points:
                    breaker_points.append([base_breakers[i].points[j - 1].x, base_breakers[i].points[j - 1].y])
                    plt.annotate( "(" + str(base_breakers[i].points[j - 1].x) + "," + str(base_breakers[i].points[j - 1].y) + ")",\
                                  (base_breakers[i].points[j - 1].x, base_breakers[i].points[j - 1].y))

                if j == len(base_breakers[i].points) - 1:
                    if [base_breakers[i].points[j].x, base_breakers[i].points[j].y] not in breaker_points:
                        breaker_points.append([base_breakers[i].points[j].x, base_breakers[i].points[j].y])
                        plt.annotate("(" + str(base_breakers[i].points[j].x) + "," + str(base_breakers[i].points[j].y) + ")",\
                                     (base_breakers[i].points[j].x, base_breakers[i].points[j].y))

        for j in range(len(fairways)):
            p1, p2 = [fairways[j].x1, fairways[j].x2], [fairways[j].y1, fairways[j].y2]
            plt.plot(p1, p2, c='g', linewidth=2, marker='.')
            # print(self.fairways[0].x1)

        #plt.figure(figsize=(4, 5))
        plt.savefig(self.configuration_label + '.png')
        plt.show()

