from datetime import datetime, timedelta

datestring = '01-01-2020 08:15:00'

date = datetime.strptime(datestring, '%d-%m-%Y %H:%M:%S')

print(date)

print(date.strftime('%Y%m%d%H%M'))

date = date + timedelta(hours=1)

print(date.strftime('%Y%m%d%H%M'))

