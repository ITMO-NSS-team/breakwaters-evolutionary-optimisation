import csv
import pandas as pd
import matplotlib.pyplot as plt

mod_id_def = "default"

indices = ['default', '1', '2', '3', '4', '11', '12', '10', '5', '9', '6', '8', '7.2', '7.1']

exps = ['default',
        '2bae29f1bf1d4b21a7c0fc45c1f48d43',
        '9b3a1e81cd694d8a892ec1aa69391a9b',
        '15cfec8f704f4d3b96fe64a89d270a2a',
        'f5ceed9e0b86467bbdf88b948582cd31',
        'MKG9_Т8_75', 'MKG10_Т6_75', 'newvar',
        '904dff5a-6946-434d-8d1d-aaa4e553e6cc',
        '5-8',
        '53b30020-35a1-49aa-a4fd-b4d68e240c23',
        'default_shpora2',
        'n7_2fix', 'n7_1']

id = "default"
line_idx = 4
line_idx2 = 6
line_idx3 = 8

with open(f'D:\\Projects\\Sochi-prichal\\breakwater-evo-opt\\img\\experiments\\{id}\\{id}-base-fortab.csv',
          newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    rowind = 0
    for row in spamreader:
        if rowind == line_idx3:
            def_values = row
        rowind += 1

ind_list = []
c1_list = []
c2_list = []
c3_list = []
r1_list = []
r2_list = []
r3_list = []

for _, exp in enumerate(exps):
    real_name = indices[_]
    id = exp
    with open(f'D:\\Projects\\Sochi-prichal\\breakwater-evo-opt\\img\\experiments\\{real_name}\\{id}-base-fortab.csv',
              newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        rowind = 0
        row_count = sum(1 for row in spamreader)

    with open(f'D:\\Projects\\Sochi-prichal\\breakwater-evo-opt\\img\\experiments\\{real_name}\\{id}-base-fortab.csv',
              newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
        rowind = 0
        for row in spamreader:
            #if (rowind == line_idx and row_count == 5) | (rowind == line_idx2 and row_count == 9) | (
             #       rowind == line_idx3 and row_count == 13):
            if rowind == line_idx3 and row_count == 13:
                ind_list.append(real_name)
                c1_list.append(round((float(def_values[0]) - float(row[0])) / float(def_values[0]) * 100))
                c2_list.append(round((float(def_values[1]) - float(row[1])) / float(def_values[0]) * 100))
                c3_list.append(round((float(def_values[2]) - float(row[2])) / float(def_values[0]) * 100))
                r1_list.append(float(row[0]))
                r2_list.append(float(row[0]))
                r3_list.append(float(row[2]))
            rowind += 1

df = pd.DataFrame({'Причал ФСО': c1_list,
                   'Паловый причал': c2_list,
                   'Причал в круизной гавани': c3_list}, index=ind_list)
ax = df.plot.bar(rot=0)
ax.set_ylabel('Improvenent, %')
ax.set_xlabel('Configuration')

for i in range(0, 14):
    ax.text([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14][i] - 0.25, c1_list[i], r1_list[i])
    ax.text([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14][i], c2_list[i], r2_list[i])
    ax.text([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13,14][i] + 0.25, c3_list[i], r3_list[i])
plt.show()
