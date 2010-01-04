"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

import re
import os
from datetime import datetime, time
from types import *

prefix = re.match("(.*)/(show|send)", os.environ['SCRIPT_URL']).group(1)

def print_header(title, styles=None):
    print 'Content-type: text/html; charset=utf-8\n'
    print '<html>'
    print '<head>'
    print '<title>' + title + '</title>'
    print '<link rel="stylesheet" type="text/css" href="',
    print prefix + '/show/stylesheet">'
    if styles:
        print styles
    print '</head>\n'
    print '<body>'
    print '<h1>' + title + '</h1>'

def print_footer():
    print '</body></html>'

def date_delta_string(my_date):
    return datetime_delta_string(datetime.combine(my_date, time()))

def datetime_delta_string(my_datetime):
    seconds = (datetime.now() - my_datetime).seconds
    minutes = seconds//60
    hours = seconds//3600
    days = (datetime.now() - my_datetime).days
    months = days//30
    years = days//365
    prefix = "vor "
    if years > 1:
        return prefix + str(years) + " Jahren"
    elif years == 1:
        return prefix + str(years) + " Jahr"
    elif months > 1:
        return prefix + str(months) + " Monaten"
    elif months == 1:
        return prefix + str(months) + " Monat"
    elif days >= 2:
        return prefix + str(days) + " Tagen"
    elif days == 1:
        return prefix + str(24*days+hours) + " Stunden"
    elif hours > 1:
        return prefix + str(hours) + " Stunden"
    elif hours == 1:
        return prefix + str(hours) + " Stunde"
    elif minutes > 1:
        return prefix + str(minutes) + " Minuten"
    elif minutes == 1:
        return prefix + str(minutes) + " Minute"
    elif seconds > 1:
        return prefix + str(seconds) + " Sekunden"
    else:
        return prefix + str(seconds) + " Sekunde"

class Tabelle:
    """Eine HTML-Tabelle"""

    def __init__(self):
        self.__columns = []
        self.__lines = []

    def addColumn(self, col):
        self.__columns.append(col)

    def addLine(self, cols):
        self.__lines.append(cols)

    def length(self):
        return len(self.__lines)

    def show(self):
        if self.length() > 0:
            print '<table class="Tabelle">'
            print '<tr>'
            for col in self.__columns:
                print '<th>' + col + '</th>'
            print '</tr>'
            for line in self.__lines:
                print '<tr>'
                for col in line:
                    if col is None:
                        col = ""
                    if type(col) in [IntType, LongType]:
                        print '<td align="right">' + str(col) + '</td>'
                    else:
                        print '<td>' + str(col) + '</td>'
                print '</tr>'
            print '</table>'
        else:
            print '(keine)'

# vim:set shiftwidth=4 expandtab smarttab:
