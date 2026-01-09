def d(up, left, up_left, alpha, beta):
    estimate = up*alpha + left*beta + (1-(alpha+beta))*up_left
    return estimate