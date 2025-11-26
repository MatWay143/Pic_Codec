def paeth_fu(u, l, ul, std_val):
    p = l + u - ul
    dl = abs(p - l)
    du = abs(p - u)
    dul = abs(p - ul)
    if dl <= du and dl <= dul:
        pred = l
    elif du <= dl and du <= dul:
        pred = u
    else:
        pred = ul
    return int(pred)
