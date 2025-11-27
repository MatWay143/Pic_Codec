import numpy as np
from typing import Callable

def _to_ints(*vals):
    return [int(np.int32(v)) for v in vals]

def opt(a, b, c):
    a, b, c = _to_ints(a, b, c)
    p = a if c >= max(a, b) else b if c <= min(a, b) else a + b - c
    return int(np.clip(p, 0, 255))

def med(a, b, c):
    a, b, c = _to_ints(a, b, c)
    p = np.median([a, b, a + b - c])
    return int(np.clip(int(p), 0, 255))

def gap(a, b, c):
    a, b, c = _to_ints(a, b, c)
    p = a + b - c
    return int(np.clip(p, 0, 255))

def paeth(a, b, c):
    a, b, c = _to_ints(a, b, c)
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    res = a if pa <= pb and pa <= pc else b if pb <= pc else c
    return int(np.clip(res, 0, 255))

def calic(a, b, c):
    return opt(a, b, c)

def loco_i(a, b, c):
    a, b, c = _to_ints(a, b, c)
    if c >= max(a, b):
        return int(np.clip(min(a, b), 0, 255))
    if c <= min(a, b):
        return int(np.clip(max(a, b), 0, 255))
    p = a + b - c
    return int(np.clip(p, 0, 255))

def avg(a, b, c):
    a, b, _ = _to_ints(a, b, c)
    p = (a + b) // 2
    return int(np.clip(p, 0, 255))

funcs = {
    "opt": opt,
    "med": med,
    "gap": gap,
    "paeth": paeth,
    "calic": calic,
    "loco_i": loco_i,
    "avg": avg
}
