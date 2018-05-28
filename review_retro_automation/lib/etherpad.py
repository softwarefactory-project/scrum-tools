#! /usr/bin/env python

import re
import requests
from datetime import datetime


HEADER = "----DO NOT EDIT ABOVE THIS LINE---"
FOOTER = "----DO NOT EDIT UNDER THIS LINE---"


class EPad(object):
    def __init__(self, base_url=None):
        self.base_url = base_url or "http://etherpad.corp.redhat.com"

    def get_pad(self, name, format=None):
        if not format:
            format = "txt"
        url = self.base_url + "/ep/pad/export/"
        url += name + "/latest?format=" + format
        pad = requests.get(url)
        trim_head = pad.text.split(HEADER)[-1]
        trim_foot = trim_head.split(FOOTER)[0]
        return trim_foot


class PadParser(EPad):
    def __init__(self, name):
        super(PadParser, self).__init__("http://etherpad.corp.redhat.com")
        self.name = name


class ReviewPadParser(PadParser):
    TOPIC_RE = re.compile('(?P<full>Regarding (?P<topic>[^:]+)\s*\:?)',
                          re.I | re.U)
    ENTRY_RE = re.compile('\s*\*\s*(?P<internal>\[internal\])?'
                          '\s*(?P<data>.+)', re.I | re.U)

    def parse(self):
        pad = self.get_pad(self.name, 'txt')
        topics = {}
        current_topic = ""
        for line in pad.split('\n'):
            if self.TOPIC_RE.match(line):
                current_topic = self.TOPIC_RE.match(line).groupdict()['topic']
                if current_topic not in topics:
                    topics[current_topic] = []
            if self.ENTRY_RE.match(line):
                entry = self.ENTRY_RE.match(line).groupdict()
                if entry['internal']:
                    entry['internal'] = True
                else:
                    entry['internal'] = False
                topics[current_topic].append(entry)
        return topics


class RetroPadParser(PadParser):
    TOPICS = ['Previous Actions',
              'Things that happened',
              'Things that went well',
              'Things that went bad',
              'Discussed Improvements',
              'Feelings safe space',
              'Recap and Actions for Next Sprint',
              'Technical Parking Lot']
    TOPIC_RE = re.compile('(?P<topic>%s)' % '|'.join(TOPICS))
    ENTRY_RE = re.compile('(?P<indent>\s*)\*\s*(?P<data>.+)', re.I | re.U)

    def parse(self):
        pad = self.get_pad(self.name, 'txt')
        topics = {}
        current_topic = ""
        try:
            for line in pad.split('\n'):
                if self.TOPIC_RE.match(line):
                    current_topic = self.TOPIC_RE.match(line).groupdict()['topic']
                    if current_topic not in topics:
                        topics[current_topic] = []
                if self.ENTRY_RE.match(line):
                    entry = self.ENTRY_RE.match(line).groupdict()
                    entry['indent'] = len(entry['indent'])
                    topics[current_topic].append(entry)
        except:
            raise Exception(line)
        return topics


class DailyPadParser(PadParser):
    DAY_RE = re.compile('^\d{4}-\d{1,2}-\d{1,2}$')
    ENTRY_RE = re.compile('#(?P<type>[\w]+)\s+(?P<author>[\w]+)'
                          '(\s+(?P<subject>[A-Za-z-_0-9]+))?\s*[:-]\s*'
                          '(?P<data>.+)', re.I | re.U)

    def parse(self):
        pad = self.get_pad(self.name, 'txt')
        days = {}
        current_day = None
        for line in pad.split('\n'):
            if self.DAY_RE.match(line):
                current_day = datetime.strptime(line, "%Y-%m-%d")
                if current_day not in days:
                    days[current_day] = []
            if self.ENTRY_RE.match(line):
                entry = self.ENTRY_RE.match(line).groupdict()
                days[current_day].append(entry)
        return days


if __name__ == "__main__":
    E = EPad('http://etherpad.corp.redhat.com')
    print E.get_pad('sfdfg-review', 'txt')
