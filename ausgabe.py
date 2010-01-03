"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

import re
import os
from types import *

prefix = re.match("(.*)/(show|send)", os.environ['SCRIPT_URL']).group(1)

def print_header(title, styles=None):
    print 'Content-type: text/html; charset=utf-8\n'
    print '<html>'
    print '<head>'
    print '<title>' + title + '</title>'
    print '<link rel="stylesheet" type="text/css" href="/show/stylesheet">'
    if styles:
        print styles
    print '</head>\n'
    print '<body>'
    print '<h1>' + title + '</h1>'

def print_footer():
    print '</body></html>'

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
