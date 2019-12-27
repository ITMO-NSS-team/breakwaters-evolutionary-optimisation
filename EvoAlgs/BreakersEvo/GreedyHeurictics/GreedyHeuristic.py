from abc import abstractmethod
import numpy as np
from CommonUtils.StaticStorage import StaticStorage


class GreedyHeurictic:
    def __init__(self):
        self.mask_index = 0

    @abstractmethod
    def init_mask(self, mask):
        return

    @abstractmethod
    def modify_mask(self, mask):
        return


class SequentialGreedyHeurictic:

    def init_mask(self, mask, max_gens):
        self.mask_index = 0

        mask[1:len(mask)] = 1
        mask[self.mask_index] = 0
        mask[self.mask_index + 1] = 0
        self.greedy_gen_step = np.floor(max_gens / len(mask) * 2)

        self.mask_index = 2

        return StaticStorage.genotype_encoder.genotype_mask

    def modify_mask(self, mask, generation_number):
        if generation_number != 0 and generation_number % self.greedy_gen_step == 0:
            if self.mask_index < len(mask):
                mask[self.mask_index - 2] = 1
                mask[self.mask_index - 1] = 1
                mask[self.mask_index] = 0
                mask[self.mask_index + 1] = 0
                self.mask_index += 2

                genotype_mask_txt = ",".join([str(int(g)) for g in mask])
                print(f'Current mask is [{genotype_mask_txt}]')
        return mask
