# coding=utf8
import numpy as np
import math


class Easing(object):
    @staticmethod
    def ease_out_bounce(x):
        n1 = 7.5625
        d1 = 2.75
        if x < 1 / d1:
            return n1 * x * x
        elif x < 2 / d1:
            x -= 1.5 / d1
            return n1 * x * x + 0.75
        elif x < 2.5 / d1:
            x -= 2.25 / d1
            return n1 * x * x + 0.9375
        else:
            x -= 2.625 / d1
            return n1 * x * x + 0.984375

    @staticmethod
    def ease_out_quad(x):
        return 1 - (1 - x) * (1 - x)

    @staticmethod
    def ease_out_quart(x):
        return 1 - pow(1 - x, 4)

    @staticmethod
    def ease_out_expo(x):
        if x == 1:
            return 1
        else:
            return 1 - pow(2, -10 * x)


def get_tracks(distance, seconds, ease_func):
    tracks = [0]
    offsets = [0]
    for t in np.arange(0.0, seconds, 0.1):
        ease = getattr(Easing, ease_func)
        offset = round(ease(t / seconds) * distance)
        tracks.append(offset - offsets[-1])
        offsets.append(offset)
    return offsets, tracks
