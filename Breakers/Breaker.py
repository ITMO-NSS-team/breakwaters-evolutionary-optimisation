from math import sqrt
from typing import List
from Configuration.Grid import BreakerPoint


def xy_to_points(xy):
    return BreakerPoint(xy[0], xy[1])


class Breaker(object):
    def __init__(self, breaker_id: str, points: List[BreakerPoint], reflection: float, base_id: str):
        self.breaker_id = breaker_id
        self.base_id = base_id
        self.points = points
        self.reflection = reflection
        assert len(self.points) > 1

    def get_length(self):
        total_length = 0
        for i in range(1, len(self.points)):
            total_length += sqrt(
                (self.points[i - 1].x - self.points[i].x) ** 2 + (self.points[i - 1].y - self.points[i].y) ** 2)
        assert total_length >= 0

        return total_length
