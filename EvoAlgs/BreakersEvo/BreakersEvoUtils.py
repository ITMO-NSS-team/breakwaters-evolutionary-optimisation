from Configuration.Grid import BreakerPoint


class BreakersEvoUtils:
    @staticmethod
    def build_breakers_from_manual_coords(coords_genotype, task):
        gen_id = 0

        new_modifications = []

        for modification in task.possible_modifications:
            point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

            for point_ind in point_ids_to_optimise_in_modification:
                modification.points[point_ind] = BreakerPoint(coords_genotype[gen_id], coords_genotype[gen_id + 1])
                gen_id += 2
            new_modifications.append(modification)
        return new_modifications

    def serialise_breakers(breakers):
        txt = []
        for pb in breakers:
            for pbp in pb.points:
                txt.append(str(int(pbp.x)))
                txt.append(str(int(pbp.y)))
        serialised = ",".join(txt)
        return serialised
