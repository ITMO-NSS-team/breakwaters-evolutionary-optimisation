import math


def average_angles(angles):
    """Average (mean) of angles

    Return the average of an input sequence of angles. The result is between
    ``0`` and ``2 * math.pi``.
    If the average is not defined (e.g. ``average_angles([0, math.pi]))``,
    a ``ValueError`` is raised.
    """

    x = sum(math.cos(a) for a in angles)
    y = sum(math.sin(a) for a in angles)

    if x == 0 and y == 0: return 0

    # To get outputs from -pi to +pi, delete everything but math.atan2() here.
    return math.fmod(math.atan2(y, x) + 2 * math.pi, 2 * math.pi)
