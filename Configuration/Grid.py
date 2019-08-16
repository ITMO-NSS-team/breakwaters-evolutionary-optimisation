class Grid:
    def __init__(self, grid_x, grid_y, spatial_step):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.spatial_step = spatial_step

    def get_coords_meter(self, point):
        return self.spatial_step * point.x, self.spatial_step * (self.grid_y - point.y)

class GridPoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class TargetPoint(GridPoint):
    def __init__(self, x, y, weight):
        super(TargetPoint, self).__init__(x, y)
        self.weight = weight


class BreakerPoint(GridPoint):
    def __init__(self, x, y):
        super(BreakerPoint, self).__init__(x, y)
