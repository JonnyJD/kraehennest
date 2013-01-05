"""Einige Klassen und Funktionen zur HTML-Ausgabe"""

import re
import os
import cgi
from datetime import date, datetime, time, timedelta
from types import IntType, LongType, StringType
from decimal import Decimal
from textwrap import dedent


######################################################################
#{ HTML-Ausgabe
######################################################################

# Prefix
prefix = '' #: Der Prefix der URL, verschiedene Authorisationsbereiche
if 'SCRIPT_URL' in os.environ:
    match = re.match("(.*)/(show|send|import)", #: internal
            os.environ['SCRIPT_URL'])
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

def redirect(url, code=302):
    """Sendet einen HTTP Redirect

    code:       
        - 301 fuer eine permanente Weiterleitung,
        - 302 als standard temporaere W.
        - 303 GET nach der Ausfuehrung von Befehlen (hier wichtig),
        - 307 temporaere Weiterleitung, bleibe bei POST

    @param code: http code (301,302,303,307)
    @type code: C{IntType}
    @param url: Die URL ohne host
    @type url: C{StringType}
    """
    if code == 301:
        print 'Status: 301 Moved Permanently'
    elif code == 302:
        print 'Status: 302 Found'
    elif code == 303:
        print 'Status: 303 See Other'
    elif code == 307:
        print 'Status: 307 Temporary Redirect'
    print 'Location: ' + url +'\n'


def print_header(title=None, styles=None):
    """Gibt den HTML-Header aus

    @param title: Titel des Dokuments
    @param styles: Die in den Header zu schreibenden styles
    """

    # http head
    print 'Content-type: text/html; charset=utf-8\n'
    if not title:
        title = "Kr&auml;hennest"
    html_head = """\
    <!DOCTYPE html>
    <html>
    <head>
    <title>%s</title>
    <meta name="robots" content="noindex, nofollow" />
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <meta http-equiv="expires" content="0" />
    <link rel="stylesheet" type="text/css" href="%s/show/stylesheet" />""" % (
            title, prefix)
    print dedent(html_head)
    if styles:
        print '<style type="text/css">\n%s\n</style>' % styles
    print '</head>\n<body>'
    if title:
        if title != "Kr&auml;hennest":
            text = "zur&uuml;ck zum Index"
            print '<div style="float:right;">%s</div>' % link("/show", text)
        print '<h1>%s</h1>' % title

def print_footer():
    """Gibt den HTML-Footer aus bzw. schliesst Body und HTML tag
    """
    print '</body>\n</html>'

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

    link = []
    if br:
        link.append('<br />')
    link.append('<a href="%s%s"' % (prefix, url))
    if color is not None:
        link.append(' style="color:%s;"' % color)
    if text is None:
        text = prefix + url
    elif type(text) != StringType:
        text = str(text)
    link.append('>%s</a>' % text)
    return "".join(link)

def print_important(message):
    """Gibt eine wichtige Nachricht gross und farbig in HTML aus
    """
    print '<h2 style="color:red">' + message + '</h2>'

def escape(string):
    """Maskiert <, > und &. Gibt (unbekannt) bei None.

    @rtype: C{StringType}
    """
    if string is None:
        return "(unbekannt)"
    else:
        return cgi.escape(string)

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
            strings = []
            strings.append('<table class="tabelle">')
            strings.append('<tr>')
            for i in range(0,len(self.__columns)):
                if self.__colspan[i] > 0:
                    strings.append('<th colspan="%d">%s</th>'
                        % (self.__colspan[i], self.__columns[i]))
                else:
                    strings.append('<th>%s</th>' %  self.__columns[i])
            strings.append('</tr>\n')
            for line in self.__lines:
                strings.append('<tr>')
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
                    strings.append("%s%s</td>" % (cell, line[i]))
                strings.append('</tr>\n')
            strings.append('</table>')
            print "".join(strings)
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

def __delta_color_string(string, delta, limit1, limit2):
    """Faerbt den String wenn der Unterschied zu jetzt
    bestimmte Grenzen erreicht.

    @param string: Zeitstring
    @param delta: Unterschied zwischen der Zeit und jetzt
    @type delta: C{timedelta}
    @param limit1: minimaler Unterschied fuer Warnfarbe
    @type limit1: C{timedelta}
    @param limit2: minimaler Unterschied fuer Alarmfarbe
    @type limit2: C{timedelta}
    @return: gefaerbter String
    @rtype: C{StringType}
    """
    if delta > limit2:
        return '<span style="color:red">%s</span>' % string
    elif delta > limit1:
        return '<span style="color:orange">%s</span>' % string
    else:
        return string


def date_delta_color_string(my_date, limit1, limit2):
    """Gibt die seit einem Datum vergangene Zeitspanne farbig aus
    
    @param my_date: betrachtes Datum
    @type my_date: C{date}
    @param limit1: minimaler Unterschied fuer Warnfarbe
    @type limit1: C{timedelta}
    @param limit2: minimaler Unterschied fuer Alarmfarbe
    @type limit2: C{timedelta}
    @return: gefaerbter String
    @rtype: C{StringType}
    """
    string = date_delta_string(my_date)
    if my_date:
        delta = date.today() - my_date
    else:
        delta = timedelta(weeks=9999)
    return __delta_color_string(string, delta, limit1, limit2)

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
            return "%s%d Jahren" % (prefix, years)
        elif years == 1:
            return "%s%d Jahr" % (prefix, years)
        elif months > 1:
            return "%s%d Monaten" % (prefix, months)
        elif months == 1:
            return "%s%d Monat" % (prefix, months)
        elif days >= 3:
            return "%s%d Tagen" % (prefix, days)
        elif days == 2:
            return "vorgestern"
        elif days == 1:
            return "gestern"
        else:
            return "heute"
    else:
        return "(unbekannt)"


def datetime_delta_color_string(my_datetime, limit1, limit2):
    """Gibt die seit einem Datum vergangene Zeitspanne farbig aus
    
    @param my_datetime: betrachter Zeitpunkt
    @type my_datetime: C{datetime}
    @param limit1: minimaler Unterschied fuer Warnfarbe
    @type limit1: C{timedelta}
    @param limit2: minimaler Unterschied fuer Alarmfarbe
    @type limit2: C{timedelta}
    @return: gefaerbter String
    @rtype: C{StringType}
    """
    string = datetime_delta_string(my_datetime)
    if my_datetime:
        delta = datetime.today() - my_datetime
    else:
        delta = timedelta(weeks=9999)
    return __delta_color_string(string, delta, limit1, limit2)

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
            return "%s%d Jahren" % (prefix, years)
        elif years == 1:
            return "%s%d Jahr" % (prefix, years)
        elif months > 1:
            return "%s%d Monaten" % (prefix, months)
        elif months == 1:
            return "%s%d Monat" % (prefix, months)
        elif days >= 2:
            return "%s%d Tagen" % (prefix, days)
        elif days == 1:
            return "%s%d Stunden" % (prefix, 24 * days + hours)
        elif hours > 1:
            return "%s%d Stunden" % (prefix, hours)
        elif hours == 1:
            return "%s%d Stunde" % (prefix, hours)
            return prefix + str(hours) + " Stunde"
        elif minutes > 1:
            return "%s%d Minuten" % (prefix, minutes)
        elif minutes == 1:
            return "%s%d Minute" % (prefix, minutes)
        elif seconds > 1:
            return "%s%d Sekunden" % (prefix, seconds)
        else:
            return "%s%d Sekunde" % (prefix, seconds)
    else:
        return "(unbekannt)"


# vim:set shiftwidth=4 expandtab smarttab:
