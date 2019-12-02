import copy
from CommonUtils.StaticStorage import StaticStorage


class BreakerStructureRepresentation:
    def __init__(self, breakers):
        self.genotype = copy.deepcopy(breakers)
        self.referenced_dataset = None

    def get_genotype_as_breakers(self):
        return self.genotype

    def get_parameterized_chromosome(self):
        genotype_encoder = StaticStorage.genotype_encoder
        return genotype_encoder.breakers_to_parameterized_genotype(self.genotype)

    def get_parameterized_chromosome_as_num_list(self):
        return [int(round(g, 0)) for g in self.get_parameterized_chromosome()]
