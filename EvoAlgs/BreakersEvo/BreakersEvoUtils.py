class BreakersEvoUtils:
    @staticmethod
    def build_breakers_from_genotype(genotype, task):
        gen_id = 0

        new_modifications = []

        for modification in task.possible_modifications:

            point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

            anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]

            for point_ind in point_ids_to_optimise_in_modification:
                modification.points[point_ind] = modification.points[point_ind].from_polar(genotype[gen_id],
                                                                                           genotype[gen_id + 1],
                                                                                           anchor_point)
                gen_id += 2
                anchor_point = modification.points[point_ind]
            new_modifications.append(modification)
        return new_modifications

    @staticmethod
    def generate_genotype_from_breakers(breakers):
        txt = []
        for pb in breakers:
            for pbp in pb.points:
                txt.append(str(int(pbp.x)))
                txt.append(str(int(pbp.y)))
        txt_genotype = ",".join(txt)
        return txt_genotype