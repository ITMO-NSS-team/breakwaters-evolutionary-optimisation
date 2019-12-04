from OptRuns.paper_exp.ExperimentalEnvironment import ExpCases, ExpEncoders, ExpAlgs, ExperimentalEnvironment

# experiment_params
task_id = ExpCases.double3
enc_id = ExpEncoders.angular
opt_id = ExpAlgs.greedy_multi

seed=42

env = ExperimentalEnvironment(seed)
env.run_optimisation_experiment(task_id, enc_id, opt_id)
