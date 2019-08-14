from collections import namedtuple


def xy_to_points(xy):
    return BreakerPoint(xy[0], xy[1])


Breaker_descr = namedtuple('Breaker_descr', ['points', 'reflection', 'base_id'])


class BreakerPoint:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Breaker:
    def __init__(self, id, breaker_descr):
        self.id = id
        self.base_id = breaker_descr.base_id
        self.points = breaker_descr.points
        self.reflection = breaker_descr.reflection
