def get_rank(point):
    """
    ランクポイントからランクを返す
    """
    if point >= 2800:
        return 10 # 10g
    elif point >= 2600:
        return 10 # 10s
    elif point >= 2400:
        return 10 # 10b
    elif point >= 2267:
        return 9 # 9g
    elif point >= 2134:
        return 9 # 9s
    elif point >= 2000:
        return 9 # 9b
    elif point >= 1933:
        return 8 # 8g
    elif point >= 1867:
        return 8 # 8s
    elif point >= 1800:
        return 8 # 8b
    elif point >= 1733:
        return 7 # 7g
    elif point >= 1667:
        return 7 # 7s
    elif point >= 1600:
        return 7 # 7b
    elif point >= 1533:
        return 6 # 6g
    elif point >= 1467:
        return 6 # 6s
    elif point >= 1400:
        return 6 # 6b
    elif point >= 1350:
        return 5 # 5g
    elif point >= 1300:
        return 5 # 5s
    elif point >= 1250:
        return 5 # 5b
    elif point >= 1200:
        return 4 # 4g
    elif point >= 1090:
        return 4 # 4s
    elif point >= 981:
        return 4 # 4b
    elif point >= 872:
        return 3 # 3g
    elif point >= 763:
        return 3 # 3s
    elif point >= 654:
        return 3 # 3b
    elif point >= 545:
        return 2 # 2g
    elif point >= 436:
        return 2 # 2s
    elif point >= 327:
        return 2 # 2b
    elif point >= 218:
        return 1 # 1g
    elif point >= 109:
        return 1 # 1s
    else:
        return 1 # 1b