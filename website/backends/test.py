import datetime
import pandas as pd

opening_time = '08:00:00'
closing_time = '20:00:00'

#start = datetime.time(8, 0, 0)
#end = datetime.time(20, 0, 0)

#print(datetime.time(8, 0, 0))
#start = pd.to_datetime('[08:00:00]', format='[%H:%M:%S]')
#end = pd.to_datetime('[20:00:00]', format='[%H:%M:%S]')

my_list = []
datelist = pd.timedelta_range(start='08:00:00', end='20:00:00', freq='0.5H').tolist()
for i in datelist:
    list1 = []
    list1.append(str(i)[7:12])
    list1.append(1)
print(my_list)

my_list = [i for i in range(1,30)]
print([i for i in range(1,30)])
