def med_fu(u, l, ul, std_val):
    if ul >= max(u, l):
        pred = min(u, l)
    elif ul <= min(u, l):
        pred = max(u, l)
    else:
        pred = u + l - ul
    return int(pred)
