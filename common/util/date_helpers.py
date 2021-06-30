import jdatetime


def get_end_day_of_jalali_month(date: jdatetime.datetime) -> int:
    month = date.month
    if month < 7:
        end_day = 31
    elif 7 <= month < 12:
        end_day = 30
    elif date.isleap():
        end_day = 30
    else:
        end_day = 29

    return end_day
