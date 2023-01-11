total_list = [1, 2, 3, 4, 5]
list_time = []
for item in range(10, 20 + 1):
    item = str(item)
    item += ':00'
    list_time.append(item)

for i in total_list:
    for j in list_time:
        print(j,i )
