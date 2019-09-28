from Configuration.Grid import BreakerPoint


class BreakersEvoUtils:
    @staticmethod
    def build_breakers_from_genotype(genotype, task, grid):
        gen_id = 0

        #print("genotype",genotype)
        new_modifications = []

        for modification in task.possible_modifications:

            point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

            anchor_point = modification.points[max(point_ids_to_optimise_in_modification) + 1]
            prev_anchor = modification.points[max(point_ids_to_optimise_in_modification) + 2]

            for point_ind in point_ids_to_optimise_in_modification:
                anchor_angle = anchor_point.point_to_relative_polar(prev_anchor)["angle"]
                length = genotype[gen_id]
                direction = (genotype[gen_id + 1] + anchor_angle + 360) % 360

                modification.points[point_ind] = modification.points[point_ind].from_polar(length,
                                                                                           direction,
                                                                                           anchor_point, grid)
                gen_id += 2
                prev_anchor = anchor_point
                anchor_point = modification.points[point_ind]
            new_modifications.append(modification)

        #print("new_modifications",new_modifications[0].points[0].x,new_modifications[0].points[0].y,new_modifications[0].points[1].x,new_modifications[0].points[1].y,new_modifications[0].points[2].x,\
              #new_modifications[0].points[2].y, "next",new_modifications[1].points[0].x,new_modifications[1].points[0].y,new_modifications[1].points[1].x,new_modifications[1].points[1].y,new_modifications[1].points[2].x,\
              #new_modifications[1].points[2].y)


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

    @staticmethod
    def build_breakers_from_coords(coords_genotype, task):
        gen_id = 0

        new_modifications = []

        for modification in task.possible_modifications:

            point_ids_to_optimise_in_modification = task.mod_points_to_optimise[modification.breaker_id]

            for point_ind in point_ids_to_optimise_in_modification:
                modification.points[point_ind] = BreakerPoint(coords_genotype[gen_id], coords_genotype[gen_id + 1])
                gen_id += 2
            new_modifications.append(modification)
        return new_modifications
