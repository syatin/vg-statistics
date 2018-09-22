def get_duration_type(duration):
    if duration < 15 * 60:
        return 10
    elif duration < 20 * 60:
        return 15
    elif duration < 25 * 60:
        return 20
    elif duration < 30 * 60:
        return 25
    else:
        return 30