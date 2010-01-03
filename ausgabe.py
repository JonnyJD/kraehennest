"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

import re
import os
from types import *

prefix = re.match("(.*)/show", os.environ['SCRIPT_URL']).group(1)

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

# vim:set shiftwidth=4 expandtab smarttab:
