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
    def save_cantidate(pop_num, objs, genotype, referenced_dataset):
        hist_file_name = f'history_{EvoAnalytics.run_id}.csv'
        if not os.path.isfile(hist_file_name):
            with open(hist_file_name, 'w', newline='') as f:
                EvoAnalytics._write_header_to_csv(f, objs, genotype, referenced_dataset)
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objs, genotype, referenced_dataset)
        else:
            with open(hist_file_name, 'a', newline='') as f:
                EvoAnalytics._write_candidate_to_csv(f, pop_num, objs, genotype, referenced_dataset)

    @staticmethod
    def _write_candidate_to_csv(f, pop_num, objs, genotype, referenced_dataset):
        writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [pop_num,referenced_dataset,','.join([str(round(_, 1)) for _ in objs]), ','.join([str(round(_, 1)) for _ in genotype])])

    @staticmethod
    def _write_header_to_csv(f, objs, genotype, referenced_dataset):
        writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["pop_num","referenced_dataset", ','.join([f'obj{_}' for _ in range(0, len(objs))]),
             ','.join([f'gen_len_{int(_/2)}' if _ % 2 == 0 else f'gen_dir_{int(_/2)}' for _ in range(0, len(genotype))])])
