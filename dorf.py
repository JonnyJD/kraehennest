#!/usr/bin/env python
"""Modul zum einlesen und ausgeben von Dorfdaten"""

#import cgitb
#cgitb.enable()

import rbdb
import util
import re
from datetime import date, datetime, timedelta
from feld import Feld
import reich
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


class Dorf(Feld):
    """Eine Klasse um Dorfdaten ein- und auszulesen.  
    """

    def fetch_data(self,
            xmin=None, xmax=None, ymin=None, ymax=None):
        """Liest die Terraindaten von der Datenbank aus."""

        self.level = 'N'
        self.crop(xmin, xmax, ymin, ymax)
        self.__get_entries()


    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank.
        
        @rtype: C{BooleanType}"""

        sql = """SELECT koords, dorfname, dorflevel, aktdatum, mauer,
                        rittername, allis.alli, alliname, allicolor, inaktiv
                FROM dorf INNER JOIN ritter ON dorf.ritternr= ritter.ritternr
                    LEFT OUTER JOIN allis ON ritter.alli=allis.allinr"""
        # so dass die andere clauses angehangen werden koennen:
        sql += " WHERE 1"
        #sql += " WHERE level='" + self.level + "'"
        #sql += self.crop_clause
        sql += self.add_cond
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            while row != None:
                match = re.search('([0-9]{3}),([0-9]{3})', row[0])
                if match:
                    x = int(match.group(1))
                    y = int(match.group(2))
                    self.entries[x,y] = {'dorfname': row[1],
                            'dorflevel': row[2], 'aktdatum': row[3],
                            'mauer': row[4], 'rittername': row[5],
                            'alliname': row[7], 'allyfarbe': row[8]}
                    if row[5] == "Keiner":
                        self.entries[x,y]["allyfarbe"] = "#00A000"
                    elif row[9] == reich.S_INAKTIV and config.is_kraehe():
                        farbe = util.color_shade('#00A000', row[8], 0.3)
                        self.entries[x,y]["allyfarbe"] = farbe
                    elif row[9] == reich.S_SCHUTZ and config.is_kraehe():
                        farbe = util.color_shade('#FFFFFF', row[8], 0.3)
                        self.entries[x,y]["allyfarbe"] = farbe
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


    def __list(self, cols, doerfer):
        """Erstellt eine Tabelle der Doerfer
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        tabelle = ausgabe.Tabelle()
        for col in cols:
            if col == "koords":
                tabelle.addColumn("X")
                tabelle.addColumn("Y")
            elif col not in ["ritternr", "allicolor"]:
                tabelle.addColumn(translate(col))
        for dorf in doerfer:
            line = []
            dorf = ausgabe.escape_row(dorf)
            for i in range(0, len(dorf)):
                if cols[i] == "koords":
                    x = dorf[i][0:3]
                    y = dorf[i][4:7]
                    link = "/show/feld/" + x + "." + y
                    line.append(ausgabe.link(link, x))
                    line.append(ausgabe.link(link, y))
                elif cols[i] == "ritternr":
                    # nachfolgenden Ritternamen verlinken
                    url = "/show/reich/" + str(dorf[i])
                    if cols[i+1] == "allicolor":
                        if dorf[i] is None:
                            link = "(nicht existent)"
                        else:
                            link = ausgabe.link(url, dorf[i+2], dorf[i+1])
                    else:
                        link = ausgabe.link(url, dorf[i+1])
                    line.append(link)
                elif cols[i] == "mauer":
                    mauer_string = {'o': "ohne", 'k': "kleine", 'm': "mittlere",
                            'g': "gro&szlig;e", 'u': "un&uuml;berwindbar",
                            'n': "?"}
                    line.append(mauer_string[dorf[i]])
                elif cols[i] == "aktdatum":
                    string = ausgabe.date_delta_string(dorf[i])
                    if dorf[i]:
                        delta = date.today() - dorf[i]
                    else:
                        delta = timedelta(weeks=9999)
                    if delta > timedelta(weeks=104):
                        zelle = '<div style="color:red">' + string + '</div>'
                        line.append(zelle)
                    elif delta > timedelta(weeks=52):
                        zelle = '<div style="color:orange">' + string + '</div>'
                        line.append(zelle)
                    else:
                        line.append(string)
                elif cols[i-1] not in ["ritternr", "allicolor"]:
                    line.append(dorf[i])
            tabelle.addLine(line)
        return tabelle

    def list_by_feld(self, x, y):
        """Holt das Dorf auf einem Feld
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["dorf.ritternr", "allicolor", "rittername", "dorfname"]
        cols += ["aktdatum", "dorflevel", "mauer"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM dorf"
        sql += " JOIN ritter ON dorf.ritternr = ritter.ritternr"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE koords = %s"
        try:
            self.cursor.execute(sql, x + ',' + y)
            armeen = self.cursor.fetchall()
            cols[0] = "ritternr" # war dorf.ritternr
            cols[5] = "level" # war dorflevel
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_by_reich(self, r_id):
        """Holt alle Doerfer eines Reiches mit r_id
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["koords", "dorfname", "aktdatum", "dorflevel", "mauer"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM dorf"
        sql += " JOIN ritter ON dorf.ritternr = ritter.ritternr"
        sql += " WHERE dorf.ritternr = %s"
        sql += " ORDER BY koords"
        try:
            self.cursor.execute(sql, r_id)
            armeen = self.cursor.fetchall()
            cols[3] = "level" # war dorflevel
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_all(self):
        """Gibt eine Tabelle aller Doerfer
        
        @return: L{Tabelle<ausgabe.Tabelle>}
        """
        return self.list_by_allianz(-1)

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
        ausgabe.print_header("Dorfliste")

        dorf = Dorf()
        dorftabelle = dorf.list_all()
        print "Anzahl D&ouml;rfer:", dorftabelle.length()
        dorftabelle.show()
    else:
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
