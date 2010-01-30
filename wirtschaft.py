#!/usr/bin/env python
"""Modul zum Einlesen und Ausgeben von Waren"""

import cgitb
cgitb.enable()

import rbdb
import util
import re
from datetime import date, datetime, timedelta
from feld import Feld
import ausgabe


def translate(column):
    """Uebersetzt den Datenbanknamen fuer die Anzeige
    
    @param column: Name in der Datenbank (oder Variable)
    @return: Anzeigename (mit HTML entities)
    @rtype: C{StringType}
    """
    dictionary = {'aktdatum': "zuletzt gesehen"}
    if column in dictionary:
        return dictionary[column]
    else:
        return column.capitalize()


class Ware(Feld):
    """Eine Klasse um Warendaten ein- und auszulesen.  
    """

    def __list(self, cols, waren):
        """Erstellt eine Tabelle der Waren
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        tabelle = ausgabe.Tabelle()
        for col in cols:
            #if col == "koords":
            #    tabelle.addColumn("X")
            #    tabelle.addColumn("Y")
            #elif col not in ["ritternr", "allicolor"]:
            tabelle.addColumn(translate(col))
        for ware in waren:
            line = []
            ware = ausgabe.escape_row(ware)
            for i in range(0, len(ware)):
                #if cols[i] == "koords":
                #    x = dorf[i][0:3]
                #    y = dorf[i][4:7]
                #    link = "/show/feld/" + x + "." + y
                #    line.append(ausgabe.link(link, x))
                #    line.append(ausgabe.link(link, y))
                #elif cols[i] == "ritternr":
                #    # nachfolgenden Ritternamen verlinken
                #    url = "/show/reich/" + str(dorf[i])
                #    if cols[i+1] == "allicolor":
                #        if dorf[i] is None:
                #            link = "(nicht existent)"
                #        elif dorf[i] == 174: # Keiner
                #            link = ausgabe.link(url, dorf[i+2], "green")
                #        else:
                #            link = ausgabe.link(url, dorf[i+2], dorf[i+1])
                #    else:
                #        link = ausgabe.link(url, dorf[i+1])
                #    line.append(link)
                #elif cols[i] == "mauer":
                #    mauer_string = {'o': "ohne", 'k': "kleine", 'm': "mittlere",
                #            'g': "gro&szlig;e", 'u': "un&uuml;berwindbar",
                #            'n': "?"}
                #    line.append(mauer_string[dorf[i]])
                #elif cols[i] == "aktdatum":
                #    string = ausgabe.date_delta_string(dorf[i])
                #    if dorf[i]:
                #        delta = date.today() - dorf[i]
                #    else:
                #        delta = timedelta(weeks=9999)
                #    if delta > timedelta(weeks=104):
                #        zelle = '<div style="color:red">' + string + '</div>'
                #        line.append(zelle)
                #    elif delta > timedelta(weeks=52):
                #        zelle = '<div style="color:orange">' + string + '</div>'
                #        line.append(zelle)
                #    else:
                #        line.append(string)
                #elif cols[i-1] not in ["ritternr", "allicolor"]:
                line.append(ware[i])
            tabelle.addLine(line)
        return tabelle

    def list_all(self):
        """Gibt eine Tabelle aller Waren aus
        
        @return: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["ware_id", "name", "preis"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM ware"
        sql += " ORDER BY ware_id ASC"

        try:
            self.cursor.execute(sql)
            waren = self.cursor.fetchall()
            return self.__list(cols, waren)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_by_allianz(self, a_id):
        """Holt alle Doerfer eines Allianz mit a_id

        @param a_id: Id der Allianz
        @type a_id: C{IntType}
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["koords", "dorf.ritternr"]
        if a_id == -1:
            cols.append("allicolor")
        cols += ["rittername", "dorfname", "aktdatum", "dorflevel", "mauer"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM dorf"
        sql += " JOIN ritter ON dorf.ritternr = ritter.ritternr"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        if a_id != -1:
            sql += " WHERE allinr = %s"
        else:
            sql += " WHERE dorf.ritternr <> 0"
        sql += " ORDER BY aktdatum DESC, allicolor, rittername, koords"
        try:
            if a_id != -1:
                self.cursor.execute(sql, a_id)
            else:
                self.cursor.execute(sql)
            armeen = self.cursor.fetchall()
            cols[1] = "ritternr" # war dorf.ritternr
            if a_id == -1:
                cols[6] = "level" # war dorflevel
            else:
                cols[5] = "level" # war dorflevel
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None


# Aufruf als Skript
if __name__ == '__main__':
    import cgi
    form = cgi.FieldStorage()

    if "list" in form:
        ausgabe.print_header("Preisliste")

        ware = Ware()
        warentabelle = ware.list_all()
        print "Anzahl Waren:", warentabelle.length()
        warentabelle.show()
    else:
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
