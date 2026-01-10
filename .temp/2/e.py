def e(left,up, up_left):
    if(left>up & up_left>left):
        estimate = up
    elif(up>left & up_left>up):
        estimate = left
    elif(left>up & up_left<up):
        estimate = left
    elif(up>left & up_left<left):
        estimate = up
    else:
        estimate = up + left - up_left
    return estimate