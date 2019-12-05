from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, TestEnvironment
import random
import numpy as np

# experiment_params
task_id = ExpCases.double3
enc_id = ExpEncoders.angular
opt_id = ExpAlgs.multi

seed = 42

np.random.seed(seed)
random.seed(seed)

env = TestEnvironment()
env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=True)
