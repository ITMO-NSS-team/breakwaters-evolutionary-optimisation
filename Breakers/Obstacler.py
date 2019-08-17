import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class Obstacler:
    index_mode = False

    def __init__(self, grid, index_mode):
        self.grid = grid
        self.index_mode = index_mode

    def get_obstacle_for_modification(self, base_breakers, modifications):
        final_obst = []
        all_modified_base_breakers_ids = []

        for i in range(0, len(modifications)):
            modification = modifications[i]

            all_modified_base_breakers_ids.append(modifications[i].base_id)
            final_obst.append(self.get_obst_for_breaker(modification))

        all_modified_base_breakers = np.unique(all_modified_base_breakers_ids)

        for j in range(0, len(base_breakers)):
            base_breaker = base_breakers[j]
            if all_modified_base_breakers != [] and base_breaker.breaker_id not in all_modified_base_breakers:
                final_obst.append(self.get_obst_for_breaker(base_breaker))

        final_obst = np.unique(final_obst)
        return final_obst

    def get_obst_for_breaker(self, breaker):
        indices = breaker.points
        obs_str = 'OBSTACLE TRANSM 0. REFL {}. LINE '.format(breaker.reflection)
        obs_ind_list = []
        for i in range(0, len(indices)):
            p_cur_ind = breaker.points[i]
            obs_ind_list.append([p_cur_ind.x, p_cur_ind.y])

            p_cur = self.grid.get_coords_meter(breaker.points[i])
            obs_str += '{},{}'.format(p_cur[0], p_cur[1])
            if i != len(indices) - 1:
                obs_str += ','

        obs_str += '#id_{}'.format(breaker.breaker_id)
        if (self.index_mode):
            return obs_ind_list
        else:
            return obs_str
