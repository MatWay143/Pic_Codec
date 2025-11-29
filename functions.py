import numpy as np

def _to_ints(*vals):
    return [int(np.int32(v)) for v in vals]

def unified_predictor(a, b, c, weights=None):
    a, b, c = _to_ints(a, b, c)
    if weights is None:
        weights = {
            "opt": 0.2,
            "med": 0.2,
            "gap": 0.15,
            "paeth": 0.2,
            "loco_i": 0.15,
            "avg": 0.1
        }
    w_opt = weights.get("opt", 0.0)
    w_med = weights.get("med", 0.0)
    w_gap = weights.get("gap", 0.0)
    w_paeth = weights.get("paeth", 0.0)
    w_loco = weights.get("loco_i", 0.0)
    w_avg = weights.get("avg", 0.0)

    p_opt = a if c >= max(a, b) else b if c <= min(a, b) else a + b - c
    p_gap = a + b - c
    p_paeth_base = a + b - c
    pa = abs(p_paeth_base - a)
    pb = abs(p_paeth_base - b)
    pc = abs(p_paeth_base - c)
    p_paeth = a if pa <= pb and pa <= pc else b if pb <= pc else c
    p_loco = (min(a, b) if c >= max(a, b) else (max(a, b) if c <= min(a, b) else a + b - c))
    p_med = int(np.median([a, b, a + b - c]))
    p_avg = (a + b) // 2

    candidates = {
        "opt": int(np.clip(p_opt, 0, 255)),
        "gap": int(np.clip(p_gap, 0, 255)),
        "paeth": int(np.clip(p_paeth, 0, 255)),
        "loco_i": int(np.clip(p_loco, 0, 255)),
        "med": int(np.clip(int(p_med), 0, 255)),
        "avg": int(np.clip(p_avg, 0, 255))
    }

    total_w = w_opt + w_med + w_gap + w_paeth + w_loco + w_avg
    if total_w <= 0:
        return int(np.clip(candidates["med"], 0, 255))

    weighted = (
        w_opt * candidates["opt"] +
        w_med * candidates["med"] +
        w_gap * candidates["gap"] +
        w_paeth * candidates["paeth"] +
        w_loco * candidates["loco_i"] +
        w_avg * candidates["avg"]
    ) / total_w

    result = int(np.round(weighted))
    return int(np.clip(result, 0, 255))
