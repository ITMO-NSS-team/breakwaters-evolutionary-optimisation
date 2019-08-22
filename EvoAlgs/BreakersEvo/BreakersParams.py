import random
import numpy as np

#TODO implement non-string genotype
class BreakersParams:

    def __init__(self, genotype_string):
        self.genotype_string = genotype_string

    def update(self, genotype_string):
        self.genotype_string = genotype_string
