# -*- coding: utf-8 -*-
import re
import codecs
import requests
import lxml
from bs4 import BeautifulSoup
import io
import datetime


hour_regex = re.compile(r"(\d+\.\d+)\s*(.*)$")

# for line in string.splitlines():
#     print(line)
#     match = hour_regex.match(line)
#     if match:
#         print([match.group(1), match.group(2)])




link = 'http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'
snapshot = 'https://web.archive.org/web/20181008002031/http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'

class Schedule():
    def __init__(self):
        self.raw_record = []

        self.to = None
        self.via = None
        self.express = False
        self.hour_list = []
        self.departures = []


        self.to_red_style = 'font-size:14.0pt;color:red'
        self.hour_red_style = [
            'color:red;mso-ansi-language:DE',
            'color:red'
        ]


    def add_information(self, string):
        self.raw_record.append(string)

    def is_express(self):

        # if self.to.text.strip() == 'Koszalin':
        #     print(self.to.text.strip(), self.to.p.b.span['style'])

        print(self.to.text.strip())
        if self.to.find('p') and self.to.p.b.span['style'] == self.to_red_style:
            return True

        for hour in self.hour_list:
            has_p = hour.find('p')
            if has_p:
                has_span = has_p.find('span')
            if has_p and has_span and hour.p.span['style'] in self.hour_red_style:
                return True
        return False

    def time_cleaner(self, string):
        if len(string) == 4:
            return '0' + string
        return string

    def process(self):
        self.to = self.raw_record[0]
        self.via = self.raw_record[1].text.strip().split(', ')
        if isinstance(self.via, str):
            self.via = [self.via]

        self.hour_list = self.raw_record[2:]
        self.express = self.is_express()
        print(self.express)

        for hour in self.hour_list:
            match = hour_regex.match(hour.text.strip())
            if match:
                time, raw_modifier = match.group(1), match.group(2)
                self.departures.append({
                    'time': self.time_cleaner(time),
                    'modifiers': list(raw_modifier.replace(' ', ''))
                })

    def to_object(self):
        print(self.via)
        return {
            'to': self.to.text.strip(),
            'via': self.via,
            'express': self.express,
            'departures': self.departures
        }


# with rb - Worked!
with open('sample/bus.html', 'r', encoding='unicode_escape') as f:
    text = f.read()
    # print(text)


soup = BeautifulSoup(text, 'html.parser')

# find valid until date
header = soup.find('span')
raw_valid_until = header.text.split()[-1].replace('r.', '')
valid_until = datetime.datetime.strptime(raw_valid_until, '%d.%m.%Y')
print(valid_until.date())



# json var
# json_dict = {}
raw_record_list = []
information_list = []
destination_list = []

# working code to select all data
main_table = soup.find('table', attrs={'class': 'MsoNormalTable'})

if not main_table:
    print('no valid table schedule found')
    exit()


table_rows = main_table.find_all('tr')
# print(len(table_rows))

# convert table row to list of column
for row in table_rows:
    all_column = row.findAll('td')
    for col in all_column:
        information_list.append(col.text.strip())
        raw_record_list.append(col)

# remove the first three element (table header)
raw_record_list = raw_record_list[3:]

list_of_schedule_object = []
schedule_instance = Schedule()
is_before_a_digit = False
for line in raw_record_list:
    a_string = line.text.strip()
    if a_string:
        is_now_a_digit = a_string[0].isdigit()
        if is_before_a_digit and not is_now_a_digit:
            list_of_schedule_object.append(schedule_instance)
            schedule_instance = Schedule()

        schedule_instance.add_information(line)
        is_before_a_digit = is_now_a_digit

# leftover
list_of_schedule_object.append(schedule_instance)

# debug: print all obtained destination
# print(len(list_of_schedule_object))
# for schedule in list_of_schedule_object:
#     print(schedule.raw_record[0].text.strip())

for schedule in list_of_schedule_object:
    schedule.process()

import pprint

pprint.pprint({
    'valid_until': str(valid_until.date()),
    'destinations': [x.to_object() for x in list_of_schedule_object]
}, indent=2)

# print({
#     'valid_until': valid_until.date(),
#     'destinations': [x.to_object() for x in list_of_schedule_object]
# })

exit()





# process it
list_to_process = information_list[3:]
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
json_string = json.dumps(information_list, ensure_ascii=False)
print(json_string)