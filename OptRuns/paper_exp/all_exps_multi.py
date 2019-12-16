import random

import numpy as np

from CommonUtils.StaticStorage import StaticStorage
from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, ExperimentalEnvironment

# experiment_params
is_local = False
StaticStorage.is_verbose = False
StaticStorage.remove_tmp = True

env = ExperimentalEnvironment()
task_id = ExpCases.double3
for i in range(0, 5):
    enc_id = ExpEncoders.angular
    opt_id = ExpAlgs.multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='final_exp1')

    ######################################
    enc_id = ExpEncoders.angular
    opt_id = ExpAlgs.verygreedy_multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='final_exp2')

    ################################
    enc_id = ExpEncoders.cartesian
    opt_id = ExpAlgs.multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='final_exp3')
    ###########################################
    enc_id = ExpEncoders.cartesian
    opt_id = ExpAlgs.verygreedy_multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='final_exp4')
