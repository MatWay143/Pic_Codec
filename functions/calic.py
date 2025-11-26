def calic_fu(u, l, ul, x, std_val):
    g1 = l - ul
    g2 = ul - u
    g3 = l - u
    gx = x - ul

    T = max(1.0, 0.25 * std_val)
    a = 1.0 + 0.5 * (abs(g1) + abs(g2) + abs(g3)) / (1.0 + std_val)

    s1 = 1.0 / (a * (1.0 + abs(g1)))
    s2 = 1.0 / (a * (1.0 + abs(g2)))
    s3 = 1.0 / (a * (1.0 + abs(g3)))
    s4 = 1.0 / (1.0 + abs(gx))

    w_sum = s1 + s2 + s3 + s4
    if w_sum == 0:
        return (u + l + ul + x) / 4.0

    w1 = s1 / w_sum
    w2 = s2 / w_sum
    w3 = s3 / w_sum
    w4 = s4 / w_sum

    pred = w1 * u + w2 * l + w3 * ul + w4 * x
    return pred
