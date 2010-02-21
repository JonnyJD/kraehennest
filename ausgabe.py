"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

import re
import os
import cgi
from datetime import date, datetime, time
from types import IntType, LongType, StringType
from decimal import Decimal


######################################################################
#{ HTML-Ausgabe
######################################################################

# Prefix
prefix = '' #: Der Prefix der URL, verschiedene Authorisationsbereiche
if 'SCRIPT_URL' in os.environ:
    match = re.match("(.*)/(show|send)", os.environ['SCRIPT_URL']) #: internal
    if match:
        prefix = match.group(1)

def test_referer(url):
    """Gleicht HTTP-Referer mit einer URL auf diesem host ab

    @param url: Die URL ohne host
    @type url: C{StringType}
    @rtype: C{BooleanType}
    """

    global message
    uri = 'http://' + os.environ['HTTP_HOST'] + url
    if "HTTP_REFERER" in os.environ:
        if os.environ['HTTP_REFERER'] == uri:
            return True
        elif os.environ['HTTP_REFERER'] == uri + "/yes":
            return True
        else:
            return False
    else:
        return False

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
    print '<meta name="robots" content="noindex, nofollow" />'
    print'<meta http-equiv="content-type" content="text/html; charset=UTF-8" />'
    print '<meta http-equiv="expires" content="0" />'
    print '<link rel="stylesheet" type="text/css" href="',
    print prefix + '/show/stylesheet" />'
    if styles:
        print '<style type="text/css">'
        print styles
        print '</style>'
    print '</head>\n'
    print '<body>'
    if title:
        if title != "Kr&auml;hennest":
            text = "zur&uuml;ck zum Index"
            print '<div style="float:right;">' + link("/show", text) + '</div>'
        print '<h1>' + title + '</h1>'

def print_footer():
    """Gibt den HTML-Footer aus bzw. schliesst Body und HTML tag
    """
    print '</body></html>'

def link(url, text=None, color=None, br=False):
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
    if text is None:
        text = prefix + url
    elif type(text) != StringType:
        text = str(text)
    link += '>' + text + '</a>'
    return link

def print_important(message):
    """Gibt eine wichtige Nachricht gross und farbig in HTML aus
    """
    print '<h2 style="color:red">' + message + '</h2>'

def escape_row(row):
    """Maskiert <, > und & in allen Elementen fuer die HTML-Ausgabe

    @type row: C{List}
    @rtype: C{List}
    """

    new_row = []
    for i in range(0, len(row)):
        if type(row[i]) == StringType:
            new_row.append(cgi.escape(row[i]))
        else:
            new_row.append(row[i])
    return new_row


class Tabelle:
    """Eine HTML-Tabelle"""

    def __init__(self):
        """Erstellt eine leere Tabelle
        """
        self.__columns = []
        self.__colspan = []
        self.__padding = []
        self.__lines = []

    def addColumn(self, col, colspan=None):
        """Fuegt eine Spalte hinzu

        @param col: Titel der Spalte
        @type col: C{StringType}
        @param colspan: Fuer wieviele Content-Spalten
        @type colspan: C{IntType}
        """
        self.__columns.append(col)
        if colspan is not None:
            self.__colspan.append(colspan)
            self.__padding.append(True)
            for i in range(1,colspan-1):
                # vorerst die inneren Columns ohne Padding "7/12 AP"
                # spaeter vielleicht eine Bool-Liste mitgeben
                self.__padding.append(False)
            self.__padding.append(True)
        else:
            self.__colspan.append(0)
            self.__padding.append(True)

    def addLine(self, cols, padding=False):
        """Fuegt eine Zeile hinzu

        Das Padding der Spalte kann nur fuer alle Zeilen abgeschaltet werden.

        @param cols: Eine Liste der Zelleintraege
        @type cols: C{List} of C{StringType}
        """
        self.__lines.append(cols)

    def length(self):
        """Anzahl der Zeilen

        @rtype: C{IntType}
        """
        return len(self.__lines)

    def show(self):
        """Gibt die Tabelle als HTML aus 
        """

        if self.length() > 0:
            print '<table class="tabelle">'
            print '<tr>'
            for i in range(0,len(self.__columns)):
                if self.__colspan[i] > 0:
                    cell = '<th colspan="' + str(self.__colspan[i]) + '">'
                    print cell + self.__columns[i] + '</th>'
                else:
                    print '<th>' + self.__columns[i] + '</th>'
            print '</tr>'
            for line in self.__lines:
                print '<tr>'
                for i in range(0,len(line)):
                    if line[i] is None:
                        line[i] = ""
                    if type(line[i]) in [IntType, LongType]:
                        cell = '<td style="text-align:right;">'
                    elif isinstance(line[i], Decimal):
                        cell = '<td style="text-align:right;">'
                    elif not self.__padding[i]:
                        cell = '<td style="padding:0px;">'
                    else:
                        cell = '<td>'
                    print cell + str(line[i]) + '</td>'
                print '</tr>'
            print '</table>'
        else:
            print '(keine)'


def confirmation(message, url):
    """Zeigt einen "Wollen sie wirklich?"-Dialog

    @param message: Nachricht/Frage
    @param url: Bei "Ja" auszufuehrender link
    """

    tabelle = Tabelle()
    tabelle.addColumn('<h2 style="color:red">'+ message + '</h2>', 2)
    line = [link(url, "Ja", "green")]
    line.append(link("javascript:back()", "Nein", "red"))
    tabelle.addLine(line)
    tabelle.show()

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
