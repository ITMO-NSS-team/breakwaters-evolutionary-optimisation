from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, ExperimentalEnvironment
import random
import numpy as np

# experiment_params
task_id = ExpCases.double3
enc_id = ExpEncoders.cartesian
opt_id = ExpAlgs.greedy_multi

seed = 42

np.random.seed(seed)
random.seed(seed)

env = ExperimentalEnvironment()
env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=True)