def b(up, left, up_left, val):
    # switch (val):
    #     case 1:
    #         estimate = left
    #     case 2:
    #         estimate = up
    #     case 3:
    #         estimate = up_left
    #     case 4:
    #         estimate = left + up - up_left
    #     case 5:
    #         estimate = left + ((up - up_left)/2)
    #     case 6:
    #         estimate = up + ((left - up_left)/2)
    #     case 7:
    #         estimate = (up + left)/2