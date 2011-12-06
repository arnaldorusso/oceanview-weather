#!/usr/bin/python

import datetime
from decimal import Decimal
import re
import urllib2
from BeautifulSoup import BeautifulSoup as bs

URL = 'http://oceanview-weather.com/index.htm'

WANTED_FIELDS = {
        'datetime': 'datetime',
        'temperature': 'temp',
        'humidity': 'humidity',
        'apparent_temperature': 'temp_app',
        'windchill': 'windchill',
}

def get_page():
    fp = urllib2.urlopen(URL)
    return bs(fp.read())

def lint_head(s):
    return s.strip().replace(' ', '_').replace('&nbsp;', '_').lower()

_val_p = re.compile('(\d+\.?\d+)')
def val_only(s):
    return Decimal(_val_p.match(s).groups()[0])

def parse_page(p):
    fields = {}

    # get date/time
    fields['datetime'] = datetime.datetime.strptime(p.find('caption').text, 
            'Conditions at local time %H:%M on %d %B %Y')

    cells = p.findAll('tr', attrs={'class': 'td_temperature_data'})

    for each in cells:
        head = None
        for i, c in enumerate(each.findAll('td')):
            if i % 2 == 0:
                head = lint_head(c.text)
            else:
                try:
                    fields[head] = val_only(c.text)
                except AttributeError:
                    print '%s: could not parse a valid value from "%s"' % (head, c.text)
                head = None

    if not verify_fields(fields):
        exit(1)

    return fields

def verify_fields(fields):
    for i in WANTED_FIELDS:
        if i not in fields:
            print '%s not found in parsed fields'
            return False
    return True


if __name__ == '__main__':
    p = get_page()
    fields = parse_page(p)
    for k, v in fields.items():
        if k not in WANTED_FIELDS:
            continue
        print WANTED_FIELDS[k], v
