from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, TestEnvironment

# experiment_params
task_id = ExpCases.double3
enc_id = ExpEncoders.cartesian
opt_id = ExpAlgs.multi

seed = 42

env = TestEnvironment(seed)
env.run_optimisation_experiment(task_id, enc_id, opt_id, run_local=True)
