# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import json
import click

import io
import datetime


regex_hour_modifier_mode_1 = re.compile(r"(\d+\.\d+)\s*(.*)$")
regex_hour_modifier_mode_2 = re.compile(r"(\d+:\d+)\s*(.*)$")


example_link = 'http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'
snapshot = 'https://web.archive.org/web/20181008002031/http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'

class Schedule():
    def __init__(self):
        self.raw_record = []

        self.to = None
        self.via = None
        self.hour_list = []
        self.departures = []

        self.to_red_style = 'font-size:14.0pt;color:red'
        self.hour_red_style = [
            'color:red;mso-ansi-language:DE',
            'color:red'
        ]


    def add_information(self, string):
        self.raw_record.append(string)

    def push_information(self, string):
        self.raw_record[-1].string = self.raw_record[-1].string + string

    def is_express(self, hour):
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

    def process_mode_1(self):
        self.to = self.raw_record[0]
        self.via = self.raw_record[1].text.strip().split(', ')
        if isinstance(self.via, str):
            self.via = [self.via]

        self.hour_list = self.raw_record[2:]

        for hour in self.hour_list:
            match = regex_hour_modifier_mode_1.match(hour.text.strip())
            if match:
                time, raw_modifier = match.group(1), match.group(2)
                self.departures.append({
                    'time': self.time_cleaner(time),
                    'modifiers': list(raw_modifier.replace(' ', '')),
                    'express': int(self.is_express(hour))
                })

    def process_mode_2(self):
        print([x.text.strip() for x in self.raw_record])
        print('ehe')

        self.to = self.raw_record[0]
        self.via = self.raw_record[1].text.strip().split(', ')
        if isinstance(self.via, str):
            self.via = [self.via]

        self.hour_list = self.raw_record[2:]

        for hour in self.hour_list:
            match = regex_hour_modifier_mode_2.match(hour.text.strip())
            if match:
                print(match.group())
                time, raw_modifier = match.group(1), match.group(2)
                self.departures.append({
                    'time': self.time_cleaner(time),
                    'modifiers': list(raw_modifier.replace(' ', '')),
                    'express': int(self.is_express(hour))
                })
        print(self.departures)

    def to_object(self):
        return {
            'to': self.to.text.strip(),
            'via': self.via,
            'departures': self.departures
        }

def scrap_mode_1(valid_until, soup, raw_record_list):
    # groups each row according to its schedule
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

    # append the leftover
    list_of_schedule_object.append(schedule_instance)

    # process the data
    for schedule in list_of_schedule_object:
        schedule.process_mode_1()

    # declaring final data
    final_data = {
        'valid_until': str(valid_until.date()),
        'destinations': [x.to_object() for x in list_of_schedule_object]
    }
    return final_data

def scrap_mode_2(valid_until, soup, raw_record_list):

    # print([x.text.strip() for x in raw_record_list])

    # groups each row according to its schedule
    list_of_schedule_object = []
    schedule_instance = Schedule()
    is_before_a_digit = False
    is_before_has_colon = False
    for index, line in enumerate(raw_record_list):
        a_string = line.text.strip()
        if a_string:

            is_now_a_digit = a_string[0].isdigit()
            is_now_has_colon = ':' in a_string

            if index < 2:
                pass
            elif is_before_has_colon:
                schedule_instance.push_information(a_string)
                is_before_has_colon = is_now_has_colon
                continue
            elif not is_before_has_colon and is_before_a_digit and not is_now_a_digit:
                list_of_schedule_object.append(schedule_instance)
                schedule_instance = Schedule()

            schedule_instance.add_information(line)
            # print([x.text.strip() for x in schedule_instance.raw_record if hasattr(x, 'text')])

            is_before_a_digit = is_now_a_digit
            is_before_has_colon = is_now_has_colon

    # append the leftover
    list_of_schedule_object.append(schedule_instance)

    # process the data
    for schedule in list_of_schedule_object:
        schedule.process_mode_2()

    return

    # declaring final data
    final_data = {
        'valid_until': str(valid_until.date()),
        'destinations': [x.to_object() for x in list_of_schedule_object]
    }
    return final_data


# @click.command()
# @click.option('--schedule_link', default=example_link, prompt='Schedule link', help = """The link that leads directly to the schedule page""")
def scaffold(schedule_link):
    """
    Scaffold HTML table formed schedule into JSON
    """
    try:
        # make a requests
        get_request = requests.get(schedule_link)
        html_text = get_request.content.decode('windows-1250')

        soup = BeautifulSoup(html_text, 'html.parser')

        # find valid until date
        valid_until = re.search(r"\d+\.\d+\.\d+", soup.text)
        if valid_until:
            valid_until = valid_until.group()
        else:
            raise ValueError("No valid date format found on header")

        valid_until = datetime.datetime.strptime(valid_until, '%d.%m.%Y')

        # variable to contains the bs4 data
        raw_record_list = []

        # select the table
        main_table = soup.find('table')
        if not main_table: raise ValueError('No Schedule table found')

        # get all table row
        table_rows = main_table.find_all('tr')
        print(len(table_rows))


        # convert table row to list of column
        for row in table_rows:
            all_column = row.findAll('td')
            for col in all_column:
                raw_record_list.append(col)

        # slice the list to include only the schedule table
        starting_index = -1
        ending_index = -1
        for col in enumerate(raw_record_list):
            if starting_index != -1 and ending_index != -1:
                break
            # print(col[1].text.strip())
            if col[1].text.strip().lower().startswith('Kierunek'.lower()):
                starting_index = col[0]
            if col[1].text.strip().lower().startswith('OZNACZENIA'.lower()):
                ending_index = col[0]

        if starting_index == -1: raise ValueError('Unable to locate the start of the table schedule')
        raw_record_list = raw_record_list[starting_index+3:(ending_index if ending_index != -1 else len(raw_record_list))]

        # cluster the page according to its mode and scrap accordingly
        cluster_key = 'Przedsiębiorstwo PKS Gryfice Sp. z o.o.'
        if cluster_key in soup.text:
            print('mode 2')
            final_data = scrap_mode_2(valid_until, soup, raw_record_list)
        else:
            print('mode 1')
            # final_data = None
            final_data = scrap_mode_1(valid_until, soup, raw_record_list)

        if not final_data:
            return

        # dump the result to json
        json_string = json.dumps(final_data, ensure_ascii=False)
        filename = 'output/{}.json'.format(str(datetime.datetime.now()).replace(':', '-').replace('.', '-'))
        with open(filename, 'w') as outputFile:
            outputFile.write(json_string)

        print('created:', filename)

    except Exception as e:
        print(e, type(e))

    print()



# link 1
# scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html')
# scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/nowogard.html')


# link 2
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/szczecin_d.html')
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/slupsk.html')
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/trzebiatow_lipa.html')
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/kolobrzeg.html')
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/ploty.html')
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/szczecin.html')
scaffold('http://www.pksgryfice.com.pl/uploads/images/rja/trzebiatow_torowa.html')