class StaticStorage:
    #convert to singletone

    base_modifications_for_tuning = []
    mod_points_to_optimise = []
    task = None
    genotype_length = 0
    exp_domain = None
    is_custom_conditions = False
    multi_objective_optimization=False

    def init(self):
        #todo implement
        return

   # @property
   # def exp_domain(self):
   #     if StaticStorage.exp_domain is not None:
   #       return StaticStorage.exp_domain