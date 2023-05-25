import re
from datetime import datetime
from datetime import timedelta
from datetime import date


some_date = "18 August 1964"

needed_format = "%Y-%m-%d"

date_format = "%d %B %Y"

try:
    date_obj = datetime.strptime(some_date, date_format)
except ValueError:
    print('Bad format')
    date_obj = None

# [1970-01-01, 2149-06-06].

start_date = date(1970, 1, 1)

end_date = date(2149, 6, 6)

print(start_date < date_obj.date() < end_date)

new_str = datetime.strftime(date_obj, needed_format)
print(new_str)