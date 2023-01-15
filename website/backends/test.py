import calendar
import datetime

# _____________________________________________________________
total_list = []
current_month = datetime.datetime.today().month
current_year = datetime.datetime.today().year

c = calendar.TextCalendar(calendar.MONDAY)
for i in c.itermonthdays(current_year, current_month):
    total_list.append(i)

total_list = list(filter(lambda num: num != 0, total_list))
# _____________________________________________________________

my_str = '10:00:00'
print(my_str.split(':00:00')[0])