"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

from types import *

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
        print '<table>'
        print '<tr>'
        for col in self.__columns:
            print '<th>' + col + '</th>'
        print '</tr>'
        for line in self.__lines:
            print '<tr>'
            for col in line:
                if col is None:
                    col = ""
                if type(col) is IntType:
                    print '<td align="right">' + str(col) + '</td>'
                else:
                    print '<td>' + str(col) + '</td>'
            print '</tr>'
        print '</table>'

# vim:set shiftwidth=4 expandtab smarttab:
