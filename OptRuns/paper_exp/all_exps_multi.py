from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, ExperimentalEnvironment
import random
import numpy as np

# experiment_params
is_local = False

seed = 42

np.random.seed(seed)
random.seed(seed)

env = ExperimentalEnvironment()
task_id = ExpCases.double3

for i in range(0, 5):


    enc_id = ExpEncoders.angular

    opt_id = ExpAlgs.multi

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local)

    opt_id = ExpAlgs.verygreedy_multi

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local)


    enc_id = ExpEncoders.cartesian

    opt_id = ExpAlgs.multi

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local)

    opt_id = ExpAlgs.verygreedy_multi

    env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=is_local)
