import csv
import datetime

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

ts = []
default = []
final = []
with open('F://gifs//hist_default.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(reader, None)
    for row in reader:
        ts.append(row[0])
        default.append(float(row[1]))
with open('F://gifs//hist_final.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(reader, None)
    for row in reader:
        final.append(float(row[1]))

tss = [datetime.datetime.strptime(t, ' %Y-%m-%d  %H:%M:%S ') for t in ts]
df = pd.DataFrame(
    {"ts": tss, "final": final, "default": default})  # , ['A','B'])

images = []
ind = 0
for ts in tss:
    plt.rcParams['axes.titlesize'] = 20
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['figure.figsize'] = [10, 7]

    ind = ind + 1
    ax = plt.subplot()
    ax.plot(df['ts'], df['default'],label="Базовый вариант")
    plt.xlabel('Дата и время', fontsize=18)
    plt.ylabel('Высота волн у причала ФСО, м.', fontsize=18)

    ax.plot(df['ts'], df['final'],label="Предложенный вариант")
    plt.axvline(x=ts, color="black")
    plt.legend(loc="upper left")

    path = f'F://gifs//ts/{ind}.png'
    plt.savefig(path, bbox_inches='tight')
    images.append(Image.open(path))

    plt.cla()
    plt.clf()
    plt.close('all')

    images[0].save(f'F://gifs//ts.gif', save_all=True,
                   append_images=images[1:], duration=250,
                   loop=0)
