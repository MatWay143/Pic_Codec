def loco_i_fu(u, l, ul, std_val):
    T = max(1.0, std_val * 0.10)
    if u == l == ul:
        return int(u)
    g1 = l - ul
    g2 = ul - u
    g3 = l - u
    def q(x):
        if x <= -2 * T:
            return -2
        if x <= -T:
            return -1
        if x < T:
            return 0
        if x < 2 * T:
            return 1
        return 2
    ctx = (q(g1) + 2) * 5 + (q(g2) + 2)
    if ul >= max(u, l):
        pred = min(u, l)
    elif ul <= min(u, l):
        pred = max(u, l)
    else:
        pred = u + l - ul
    if abs(g1) > 2 * T and abs(g2) <= T:
        pred = l
    elif abs(g2) > 2 * T and abs(g1) <= T:
        pred = u
    else:
        if abs(g1) <= T and abs(g2) <= T and abs(g3) <= T:
            pred = round((u + l + ul) / 3.0)
    pred = int(pred)
    if pred < 0:
        pred = 0
    elif pred > 255:
        pred = 255
    return pred
