from abc import ABCMeta, abstractmethod
import numpy as np
import os
from more_itertools import numeric_range
from sympy import Line, Point, Segment,intersection
import re
import matplotlib.pyplot as plt
from Simulation.Results import WaveSimulationResult
from Simulation.ConfigurationStrategies import ConfigurationInfo


class SimulationStrategyAbstract(metaclass=ABCMeta):

    @abstractmethod
    def simulate(self, configuration_info: ConfigurationInfo):
        return


class SimpleGeomSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):

        stop=0
        hs = np.zeros(shape=(configuration_info.domain.model_grid.grid_y, configuration_info.domain.model_grid.grid_x))
        self.heatmap2d(hs,configuration_info.domain.base_breakers)

        if stop==1:
            return WaveSimulationResult(hs)


        if configuration_info.domain.wind_direction==0 or configuration_info.domain.wind_direction==180:
            p1=Point(0,1)
        elif configuration_info.domain.wind_direction==45 or configuration_info.domain.wind_direction==225:
            p1 = Point(1, 1)
        elif configuration_info.domain.wind_direction==90 or configuration_info.domain.wind_direction==270:
            p1 = Point(1, 0)
        elif configuration_info.domain.wind_direction==135 or configuration_info.domain.wind_direction==315:
            p1 = Point(1, -1)
        else:
            print("Incorrect angle")
            return 0

        wind_line = Line(Point(0, 0), p1)


        #num_of_iteration=0

        for i in numeric_range(0,configuration_info.domain.model_grid.grid_x):

            for j in numeric_range(0,configuration_info.domain.model_grid.grid_y):


                if Point(i,j) in wind_line:
                    hs[j][i]=self.WaveHeight(wind_line,configuration_info.domain.base_breakers,{"x":i,"y":j},configuration_info.domain.wind_direction,\
                                             configuration_info.domain.max_height_of_wave)
                else:
                    parallel_line_of_wind=wind_line.parallel_line([i,j])

                    hs[j][i]=self.WaveHeight(parallel_line_of_wind, configuration_info.domain.base_breakers, {"x": i, "y": j},configuration_info.domain.wind_direction,\
                                             configuration_info.domain.max_height_of_wave)

                #num_of_iteration+=1
                #print(num_of_iteration)

        with open('out.txt', 'w') as out:
            for i in range(len(hs)):
                for j in range(len(hs[0])):
                    out.write('{}    '.format(hs[i][j]))
                out.write("\r\n")

        self.heatmap2d(hs,configuration_info.domain.base_breakers)



        return WaveSimulationResult(hs)

    def heatmap2d(self,arr: np.ndarray,base_breakers):
        plt.imshow(arr, cmap='viridis')
        plt.colorbar()


        for i in range(len(base_breakers)):
            for j in range(1,len(base_breakers[i].points)):
                p1,p2=[base_breakers[i].points[j-1].x,base_breakers[i].points[j].x],\
                       [base_breakers[i].points[j-1].y,base_breakers[i].points[j].y]
                plt.plot(p1, p2,c='r',linewidth=2)

            for j in range(len(base_breakers[i].points)):
                if j==len(base_breakers[i].points)-1:
                    plt.annotate("(" + str(p1[1]) + "," + str(p2[1]) + ")", (p1[1], p2[1]))
                else:
                    plt.annotate("(" + str(p1[0]) + "," + str(p2[0]) + ")", (p1[0], p2[0]))


        plt.show()

    def WaveHeight(self,wind_line,base_breakers,point,wind_direction,max_height_of_wave):

        heights_list=[]
        for i in range(len(base_breakers)):
            for j in range(1,len(base_breakers[i].points)):

                p1,p2=(Point(base_breakers[i].points[j-1].x,base_breakers[i].points[j-1].y),\
                       Point(base_breakers[i].points[j].x,base_breakers[i].points[j].y))
                breaker_line=Segment(p1,p2)
                intersection_between_wind_and_breaker = intersection(breaker_line, wind_line)

                if intersection_between_wind_and_breaker == []:
                    heights_list.append(max_height_of_wave)

                elif intersection_between_wind_and_breaker != []:

                    intersection_between_wind_and_breaker=intersection_between_wind_and_breaker[0]

                    if re.search(r'\bLine2D\b', str(type(intersection_between_wind_and_breaker))) or re.search(r'\bSegment2D\b', str(type(intersection_between_wind_and_breaker))):

                        if Point(point["x"],point["y"]) in  Segment(intersection_between_wind_and_breaker.points[0], \
                                                                    intersection_between_wind_and_breaker.points[1]):

                            heights_list.append(0)


                        else:
                            print(breaker_line)
                            if wind_direction == 0:
                                if float(breaker_line.points[0].y) > point["y"]:

                                    heights_list.append(breaker_line.distance(Point(point["x"],point["y"])))

                                else:
                                    heights_list.append(max_height_of_wave)

                            elif wind_direction > 0 and wind_direction < 180:
                                if float(breaker_line[0].x) > point["x"]:
                                    heights_list.append(breaker_line.distance(Point(point["x"],point["y"])))
                                else:
                                    heights_list.append(max_height_of_wave)

                            elif wind_direction == 180:
                                if float(breaker_line.points[0].y) < point["y"]:
                                    heights_list.append(breaker_line.distance(Point(point["x"],point["y"])))
                                else:
                                    heights_list.append(max_height_of_wave)

                            elif wind_direction > 180 and wind_direction < 360:
                                if float(breaker_line.points[0].x) < point["x"]:

                                    heights_list.append(breaker_line.distance(Point(point["x"],point["y"])))
                                else:

                                    heights_list.append(max_height_of_wave)

                            #intersection_between_wind_and_breaker = {"x": float(intersection_between_wind_and_breaker.points[index_of_point].x), \
                                        #"y": float(intersection_between_wind_and_breaker.points[index_of_point].y)}

                            #heights_list.append(np.linalg.norm(np.array([intersection_between_wind_and_breaker["x"], \
                                                                         #intersection_between_wind_and_breaker["y"]]) - np.array([point["x"], point["y"]])))

                    else:
                        intersection_between_wind_and_breaker = {"x": float(intersection_between_wind_and_breaker.x),\
                                                                "y": float(intersection_between_wind_and_breaker.y)}

                        marker = 0
                        if wind_direction==0:
                            if intersection_between_wind_and_breaker["y"]<point["y"]:
                                heights_list.append(max_height_of_wave)
                                marker=1
                        elif wind_direction>0 and wind_direction<180:
                            if intersection_between_wind_and_breaker["x"]<point["x"]:
                                heights_list.append(max_height_of_wave)
                                marker=1
                        elif wind_direction==180:
                            if intersection_between_wind_and_breaker["y"]>point["y"]:
                                heights_list.append(max_height_of_wave)
                                marker=1
                        elif wind_direction >180 and wind_direction<360:
                            if intersection_between_wind_and_breaker["x"]>point["x"]:
                                heights_list.append(max_height_of_wave)
                                marker=1

                        if marker==0:
                            heights_list.append(np.linalg.norm(np.array([intersection_between_wind_and_breaker["x"], \
                                                                         intersection_between_wind_and_breaker["y"]]) - np.array([point["x"], point["y"]])))

        return min(heights_list)



class SwanSimulationStrategy(SimulationStrategyAbstract):
    def simulate(self, configuration_info):
        if not os.path.isfile(
                'D:\\SWAN_sochi\\r\\hs{}.d'.format(configuration_info.configuration_label)):
            print("SWAN RUNNED")
            os.system(r'swanrun.bat {}'.format(configuration_info.info))
            NotImplementedError
            print("SWAN FINISHED")
        #else:
            #print("FILE {} EXISTS".format(configuration_info.configuration_label))


        hs = np.genfromtxt('D:\\SWAN_sochi\\r\\hs{}.d'.format(configuration_info.configuration_label))

        return WaveSimulationResult(hs)
