import numpy as np


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

    def from_polar(self, length, direction, anchor_point, grid):
        rad_grad = 180 / np.pi
        x = int(round(length * np.sin(direction / rad_grad) + anchor_point.x))
        y = int(round(length * np.cos(direction / rad_grad) + anchor_point.y))

        # TODO real grid size
        self.x = max(min(x, grid.grid_x), 0)
        self.y = min(min(y, grid.grid_y), 0)

        return BreakerPoint(x, y)

    def get_relative_polar_coordinates(self, anchor_point):

        rad_grad = 180 / np.pi

        angle = 0

        assert anchor_point.x > -1 and anchor_point.y > -1

        if self.x == -1:
            x = 0
        else:
            x = self.x - anchor_point.x

        if self.x == -1:
            y = 0
        else:
            y = self.y - anchor_point.y

        length = np.sqrt(x ** 2 + y ** 2)

        if x > 0 and y > 0:
            angle = np.arctan(x / y) * rad_grad
        if (x > 0 and y < 0) or (x < 0 and y < 0):
            angle = np.arctan(x / y) * rad_grad + 180
        if x < 0 and y > 0:
            angle = np.arctan(x / y) * rad_grad + 360

        if x > 0 and y == 0:
            angle = 90
        if x < 0 and y == 0:
            angle = 270

        if x == 0 and y > 0:
            angle = 0
        if x == 0 and y < 0:
            angle = 180

        if angle < 0:
            angle = angle + 360

        return {"length": length, "angle": angle}
