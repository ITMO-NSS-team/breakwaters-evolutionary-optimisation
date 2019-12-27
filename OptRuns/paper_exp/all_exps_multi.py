import random
import re
import numpy as np

from CommonUtils.StaticStorage import StaticStorage
from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, ExperimentalEnvironment

# experiment_params
is_vis = True
is_local = True
StaticStorage.is_verbose = False
StaticStorage.remove_tmp = True

env = ExperimentalEnvironment()
task_id = ExpCases.double3
for i in range(0, 5):
    enc_id = ExpEncoders.angular
    #print("Name of value", str(enc_id).rsplit('.', 2)[1] )

    opt_id = ExpAlgs.multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='exp1', is_vis=is_vis)

    ######################################
    enc_id = ExpEncoders.angular
    opt_id = ExpAlgs.verygreedy_multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='exp2', is_vis=is_vis)

    ################################
    enc_id = ExpEncoders.cartesian
    opt_id = ExpAlgs.multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='exp3', is_vis=is_vis)
    ###########################################
    enc_id = ExpEncoders.cartesian
    opt_id = ExpAlgs.verygreedy_multi

    seed = 42 + i
    np.random.seed(seed)
    random.seed(seed)

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local, add_label='exp4', is_vis=is_vis)
