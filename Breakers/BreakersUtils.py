import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class BreakersUtils:
    @staticmethod
    def merge_breakers_with_modifications(base_breakers, modifications):
        final_breakers = []
        all_modified_base_breakers_ids = []

        for modification in modifications:
            all_modified_base_breakers_ids.append(modification.base_id)
            final_breakers.append(modification)

        all_modified_base_breakers = np.unique(all_modified_base_breakers_ids)

        for base_breaker in base_breakers:
            if all_modified_base_breakers != [] and base_breaker.breaker_id not in all_modified_base_breakers:
                final_breakers.append(base_breaker)

        return final_breakers
