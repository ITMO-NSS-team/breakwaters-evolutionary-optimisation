class StaticStorage:
    base_modifications_for_tuning = []
    mod_points_to_optimise = []
    task = None
    genotype_length = 0
    exp_domain = None
    is_custom_conditions = False
    is_verbose=False
    multi_objective_optimization = False
    mean_hhs = []
    costs = []
    remove_tmp=None
    genotype_encoder=None
    max_gens=None
