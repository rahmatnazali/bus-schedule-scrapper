# -*- coding: utf-8 -*-
import re
import requests
from bs4 import BeautifulSoup
import json
import click

import io
import datetime


regex_hour_modifier = re.compile(r"(\d+\.\d+)\s*(.*)$")


example_link = 'http://www.pksgryfice.com.pl/uploads/images/rja/gryfice.html'
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

        for hour in self.hour_list:
            match = regex_hour_modifier.match(hour.text.strip())
            if match:
                time, raw_modifier = match.group(1), match.group(2)
                self.departures.append({
                    'time': self.time_cleaner(time),
                    'modifiers': list(raw_modifier.replace(' ', ''))
                })

    def to_object(self):
        return {
            'to': self.to.text.strip(),
            'via': self.via,
            'express': int(self.express),
            'departures': self.departures
        }

@click.command()
@click.option('--schedule_link', default=example_link, prompt='Schedule link', help = """The link that leads directly to the schedule page""")
def scaffold(schedule_link):
    """
    Scaffold HTML table formed schedule into JSON
    """
    try:
        # make a requests
        get_request = requests.get(schedule_link)
        soup = BeautifulSoup(get_request.text, 'html.parser')

        # find valid until date
        html_page_header = soup.find('span')
        if not html_page_header: raise ValueError('Page header format has changed')
        raw_valid_until = html_page_header.text.split()[-1].replace('r.', '')
        valid_until = datetime.datetime.strptime(raw_valid_until, '%d.%m.%Y')

        # variable to contains the bs4 data
        raw_record_list = []

        # select the table
        main_table = soup.find('table', attrs={'class': 'MsoNormalTable'})
        if not main_table: raise ValueError('Schedule table format has changed')

        # get all table row
        table_rows = main_table.find_all('tr')

        # convert table row to list of column
        for row in table_rows:
            all_column = row.findAll('td')
            for col in all_column:
                raw_record_list.append(col)

        # remove the first three element (table header)
        raw_record_list = raw_record_list[3:]

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
            schedule.process()

        # declaring final data
        final_data = {
            'valid_until': str(valid_until.date()),
            'destinations': [x.to_object() for x in list_of_schedule_object]
        }

        # dump the result to json
        json_string = json.dumps(final_data, ensure_ascii=False)
        filename = 'output/{}.json'.format(str(datetime.datetime.now()).replace(':', '-').replace('.', '-'))
        with open(filename, 'w') as outputFile:
            outputFile.write(json_string)

        print('created:', filename)

    except Exception as e:
        print(e, type(e))



scaffold()