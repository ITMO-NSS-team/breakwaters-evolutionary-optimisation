import os
import csv


class EvoAnalytics:
    run_id = "opt_0"

    @staticmethod
    def clear():
        hist_file_name = f'history_{EvoAnalytics.run_id}.csv'
        if os.path.isfile(hist_file_name):
            os.remove(hist_file_name)

    @staticmethod
    def save_cantidate(pop_num, objs, genotype):
        hist_file_name = f'history_{EvoAnalytics.run_id}.csv'
        if not os.path.isfile(hist_file_name):
            with open(hist_file_name, 'w', newline='') as f:
                EvoAnalytics._write_header_to_csv(f, objs, genotype)
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objs, genotype)
        else:
            with open(hist_file_name, 'a', newline='') as f:
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objs, genotype)

    @staticmethod
    def _write_candidate_to_csv(f, pop_num, objs, genotype):
        #Количество значений целевых функций
        #print("objs",objs)
        writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [pop_num, ','.join([str(round(_, 1)) for _ in objs]), ','.join([str(round(_, 1)) for _ in genotype])])

    @staticmethod
    def _write_header_to_csv(f, objs, genotype):

        writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["pop_num", ','.join([f'obj{_}' for _ in range(0, len(objs))]),
             ','.join([f'gen_len_{int(_/2)}' if _ % 2 == 0 else f'gen_dir_{int(_/2)}' for _ in range(0, len(genotype))])])

    @staticmethod
    def change_symbol_in_file(f,symbol=',',symbol_for_change=';'):
        with open(f.name, 'r+') as f:
            txt = f.read().replace(symbol_for_change, symbol)
            f.seek(0)
            f.truncate()
            f.write(txt)







