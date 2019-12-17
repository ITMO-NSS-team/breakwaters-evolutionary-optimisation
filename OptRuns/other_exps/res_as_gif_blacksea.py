import os
import datetime
import os
from PIL import Image
import numpy as np

from CommonUtils.StaticStorage import StaticStorage
from Configuration.Domains import BlackSea
from Optimisation.Optimiser import ParetoEvolutionaryOptimiser
from Simulation.WaveModel import SwanWaveModel
from Visualisation.ModelVisualization import ModelsVisualization

exp_domain = BlackSea()
StaticStorage.exp_domain = exp_domain

wave_model = SwanWaveModel(exp_domain, None)

optimiser = ParetoEvolutionaryOptimiser()

max2 = 1.1

wave_model.output_time_step = 1
# default
# final
real_name = 'BlackSea'

def rotate_90_degree_clckwise(matrix):
    new_matrix = []
    for i in range(len(matrix[0])):
        li = list(map(lambda x: x[i], matrix))
        li.reverse()
        new_matrix.append(li)

    return new_matrix


def angle_to_xy(direction, hs):
    from copy import  copy
    length = copy(hs)
    length[length == -9] = 0
    length = length/12
    rad_grad = 180 / np.pi
    x = length * np.sin(direction / rad_grad)
    y = length * np.cos(direction / rad_grad)
    return x, y

images=[]


for _, mod_id in enumerate([real_name]):

    if not os.path.isdir(f'img/experiments/{real_name}'):
        os.mkdir(f'img/experiments/{real_name}')

    hs_base = np.genfromtxt(f'F:\\gifs\\dir\\HSig.dat')  # , skip_header=130*100,max_rows=(142-80)*130)
    dir_base = np.genfromtxt(f'F:\\gifs\\dir\\DIR.dat')  # , skip_header=130*100,max_rows=(142-80)*130)

    base_date = datetime.datetime(2016, 1, 3, 8, 0, 0)
    ts_ind = 1
    #rng = range(80 - 24+24, 142 - 24+24)
    rng = range(8, 8 + 63)

    for ts in rng:  # range(8760+80, 8760+81):#142):
        print(ts)

        wave_model.output_time_step = ts

        label_to_reference = f'HSig'

        ts = wave_model.output_time_step
        start = (ts_ind - 1) * exp_domain.model_grid.grid_y
        end = ts_ind * exp_domain.model_grid.grid_y
        hs = hs_base[start:end]
        dir = dir_base[start:end]

        hs[hs != -9] = hs[hs != -9] / 1.81 * 1.22
        #hs = np.flipud(hs)
        #dir = np.flipud(dir)

        u, v = angle_to_xy(dir, hs)
        # hs = np.asarray(rotate_90_degree_clckwise(hs))
        visualiser = ModelsVisualization(ts, mod_id)
        path=visualiser.experimental_visualise_large(hs, u, v, max2, base_date)

        images.append(Image.open(path))

        ts_ind = ts_ind + 1
        base_date = base_date + datetime.timedelta(hours=1)

    images[0].save(f'F://gifs//{real_name}.gif', save_all=True,
                   append_images=images[1:], duration=250,
                   loop=0)