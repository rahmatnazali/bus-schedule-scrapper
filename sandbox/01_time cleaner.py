l = [
    '6.40',
    '06.40',
]

def time_cleaner(string):
    if len(string) == 4:
        return '0' + string
    return string

for time in l:
    print(time_cleaner(time))