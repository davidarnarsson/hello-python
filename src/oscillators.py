from math import sin, pow, pi, atan, tan, floor


def __cot(x):
    return 1 / (tan(x) + 0.000001)


def sine(t, note):
    return sin(pi * t * note)


def saw(t, note):
    return atan(__cot(t * note * pi / -2))


def square(t, note):
    return (2 * ((2 * floor(t * note)) - floor(2 * t * note))) + 1
