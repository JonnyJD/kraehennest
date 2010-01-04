#!/usr/bin/python

#import cgitb
#cgitb.enable()

import rbdb
import util
import re
from datetime import date, datetime, timedelta
from feld import Feld
import ausgabe

class Dorf(Feld):
    """Eine Klasse um Dorfdaten ein- und auszulesen.
    
    Einlesen:
        Mit queue_entry(fields) werden die Felder einzeln uebergeben.
        Mit exec_queue() werden dann alle eingetragen, falls nicht vorhanden.

    Auslesen:
        Mit set_add_cond() kann man eine weitere Bedingung vorgeben.
        Danach wird mit fetch_data([level[, xmin[, xmax[, ymin[, ymax]]]]])
        alles passende von der Datenbank geladen.
        Mit has(x,y) und get(x,y) kann man dann einzeln zugreifen.
    
    Beenden:
        Mit disconnect() kann die Datenbankverbindung beendet werden.
        Danach koennen nurnoch die bereits geladenen Daten geholt werden."""

    def fetch_data(self,
            xmin=None, xmax=None, ymin=None, ymax=None):
        """Liest die Terraindaten von der Datenbank aus."""

        self.level = 'N'
        self.crop(xmin, xmax, ymin, ymax)
        self.__get_entries()


    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank."""

        sql = """SELECT koords, dorfname, dorflevel, aktdatum, mauer,
                        rittername, allis.alli, alliname, allicolor
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
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


    def __list(self, cols, doerfer):
        tabelle = ausgabe.Tabelle()
        for col in cols:
            if col == "koords":
                tabelle.addColumn("x")
                tabelle.addColumn("y")
            elif col not in ["ritternr", "allicolor"]:
                tabelle.addColumn(col)
        for dorf in doerfer:
            line = []
            for i in range(0, len(dorf)):
                if cols[i] == "koords":
                    line.append(dorf[i][0:3])
                    line.append(dorf[i][4:7])
                elif cols[i] == "ritternr":
                    # nachfolgenden Ritternamen verlinken
                    col = '<a href="' + ausgabe.prefix + '/show/reich/'
                    col += str(dorf[i]) + '"'
                    if cols[i+1] == "allicolor":
                        if dorf[i] == 174: # Keiner
                            col += ' style="color:green"'
                        else:
                            col += ' style="color:' + dorf[i+1] + '"'
                        col += '>' + dorf[i+2] + '</a>'
                    else:
                        col += '>' + dorf[i+1] + '</a>'
                    line.append(col)
                elif cols[i] == "mauer":
                    mauer_string = {'o': "ohne", 'k': "kleine", 'm': "mittlere",
                            'g': "gro&szlig;e", 'u': "un&uuml;berwindbar",
                            'n': "?"}
                    line.append(mauer_string[dorf[i]])
                elif cols[i] == "aktdatum":
                    string = ausgabe.date_delta_string(dorf[i])
                    delta = date.today() - dorf[i]
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
        """Holt das Dorf auf einem Feld"""

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
            return False

    def list_by_reich(self, r_id):
        """Holt alle Doerfer eines Reiches mit r_id"""

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
            return False

    def list_all(self):
        return self.list_by_allianz(-1)

    def list_by_allianz(self, a_id):
        """Holt alle Doerfer eines Allianz mit a_id"""

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
            return False


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
