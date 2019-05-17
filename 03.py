# -*- coding: utf-8 -*-

import codecs
import requests
import lxml
from bs4 import BeautifulSoup
import io

link = 'http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'
snapshot = 'https://web.archive.org/web/20181008002031/http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'

# with rb - Worked!
with open('sample/bus.html', 'r', encoding='unicode_escape') as f:
    text = f.read()
    # print(text)

soup = BeautifulSoup(text, 'html.parser')

# json var
json_dict = {}
json_list = []


# working code to select all data
main_table = soup.find('table', attrs={'class': 'MsoNormalTable'})
# print(main_table)
tr = main_table.find_all('tr')
print(len(tr))
for row in tr:
    # first_column = row.findAll('td')[0].text
    # second_column = row.findAll('td')[1].text
    # third_column = row.findAll('td')[2].text
    # print(first_column, second_column, third_column)

    all_column = row.findAll('td')
    for col in all_column:
        # print(col.text)
        json_list.append(col.text.strip())


# process it
list_to_process = json_list[3:]
print(list_to_process)

processed_list = []

to = None
via = None
express = False
departures = []

for line in list_to_process:
    if line:
        # print(line)
        if line[0].isalpha() and to is not None:
            # add the whole data to processed_list
            # reset all
            print(to)
            print(via)
            print(express)
            print(departures)

            to = None
            via = None
            express = False
            departures = []

            pass
        elif line[0].isalpha():
            if to is None:
                to = line
            elif via is None:
                via = line
        else:
            splitted_modifier = line.split()
            if len(splitted_modifier) > 1:
                back_modifier = splitted_modifier[1]
                departures.append({
                    'time': splitted_modifier[0].strip(),
                    'modifiers': list(back_modifier)
                })
        # print(line, line[0].isdigit())

# dump it!
import json
json_string = json.dumps(json_list, ensure_ascii=False)
print(json_string)