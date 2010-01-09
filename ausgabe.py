"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

import re
import os
from datetime import date, datetime, time
from types import *


######################################################################
#{ HTML-Ausgabe
######################################################################

# Prefix
if 'SCRIPT_URL' in os.environ:
    prefix = re.match("(.*)/(show|send)", os.environ['SCRIPT_URL']).group(1)
else:
    prefix = '' #: Der Prefix der URL, verschiedene Authorisationsbereiche


def print_header(title=None, styles=None):
    """Gibt den HTML-Header aus

    @param title: Titel des Dokuments
    @param styles: Die in den Header zu schreibenden styles
    """

    print 'Content-type: text/html; charset=utf-8\n'
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
    print '          "http://www.w3.org/TR/html4/loose.dtd">'
    print '<html>'
    print '<head>'
    if title:
        print '<title>' + title + '</title>'
    print '<link rel="stylesheet" type="text/css" href="',
    print prefix + '/show/stylesheet">'
    if styles:
        print styles
    print '</head>\n'
    print '<body>'
    if title:
        print '<h1>' + title + '</h1>'

def print_footer():
    """Gibt den HTML-Footer aus bzw. schliesst Body und HTML tag
    """
    print '</body></html>'

def link(url, text, color=None, br=False):
    """Gibt ein gefuelltes HTML-A-Tag zurueck.
    
    Bei Bedarf mit nem C{BR} davor und dem Prefix wenn noetig.
    Auch eine Farbe kann man festlegen.

    @param url: Das absolute Linkziel
    @param text: Der Linktext
    @param color: Die Linkfarbe (Name oder Hexcode)
    @param br: Ob ein C{BR} davorgeschrieben werden sollte
    @type br: C{BooleanType}
    @return: Die HTML-tags
    @rtype: C{StringType}
    """

    link = ''
    if br:
        link += '<br />'
    link += '<a href="' + prefix + url + '"'
    if color is not None:
        link += ' style="color:' + color + ';"'
    link += '>' + text + '</a>'
    return link


class Tabelle:
    """Eine HTML-Tabelle"""

    def __init__(self):
        """Erstellt eine leere Tabelle
        """
        self.__columns = []
        self.__lines = []

    def addColumn(self, col):
        """Fuegt eine Spalte hinzu

        @param col: Titel der Spalte
        """
        self.__columns.append(col)

    def addLine(self, cols):
        """Fuegt eine Zeile hinzu

        @param cols: Eine Liste der Zelleintraege
        """
        self.__lines.append(cols)

    def length(self):
        """Anzahl der Zeilen
        """
        return len(self.__lines)

    def show(self):
        """Gibt die Tabelle als HTML aus"""

        if self.length() > 0:
            print '<table class="tabelle">'
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

######################################################################
#{ Datumsformatierung
######################################################################

def date_delta_string(my_date):
    """Gibt die seit einem Datum vergangene Zeitspanne aus
    
    @rtype: C{StringType}
    """

    if my_date:
        days = (date.today() - my_date).days
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
        elif days >= 3:
            return prefix + str(days) + " Tagen"
        elif days == 2:
            return "vorgestern"
        elif days == 1:
            return "gestern"
        else:
            return "heute"
    else:
        return "(unbekannt)"

def datetime_delta_string(my_datetime):
    """Gibt die seit Einer Zeit vergangene Zeitspanne aus

    @rtype: C{StringType}
    """

    if my_datetime:
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
    else:
        return "(unbekannt)"


# vim:set shiftwidth=4 expandtab smarttab:
