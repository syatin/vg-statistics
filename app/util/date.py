from datetime import timedelta

def get_week_start_date(d):
    """
    与えられた日付の週始めの0時0分0秒を返す
    """
    monday = d - timedelta(days=-d.weekday())
    week_start_date = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    return week_start_date