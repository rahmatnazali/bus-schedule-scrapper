# -*- coding: utf-8 -*-

import codecs
import requests
import lxml
from bs4 import BeautifulSoup
import io

link = 'http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'
snapshot = 'https://web.archive.org/web/20181008002031/http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'


# get = requests.get(link)
# print(get.text)

# open with codecs, fail
# f = codecs.open('sample/01_gryfice.html', 'r', 'utf-8')
# for line in f:
#     print(f)

# withh io.open
# with io.open('sample/01_gryfice.html', encoding='utf-8') as f:
#     for line in f:
#         print(line)


# with rb - Worked!
with open('sample/01_gryfice.html', 'r', encoding='unicode_escape') as f:
    text = f.read()
    # print(text)
    # for line in text:
    #     print(line)

soup = BeautifulSoup(text, 'html.parser')


# current working
# soup = BeautifulSoup(open('sample/01_gryfice.html', encoding='utf-8', errors='ignore'), 'html.parser')

# soup = BeautifulSoup(open('sample/01_gryfice.html', encoding='ISO-8859-1', errors='ignore'), 'html.parser')
# soup = BeautifulSoup(open('sample/01_gryfice.html', encoding='latin-1', errors='ignore'), 'html.parser')

# print(soup)

# res = soup.find_all('span')
# for el in res:
#     print(el.text)
# print(res)

# Kierunek = soup.find_all('span', attrs={'style': 'font-size:14.0pt'})
# print(res)
# for el in Kierunek:
#     print(el.text)




# json dump
a_list = []

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
        a_list.append(col.text.strip())


# process it
list_to_process = a_list[3:]
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
json_string = json.dumps(a_list, ensure_ascii=False)
print(json_string)