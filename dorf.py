#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
import re
from feld import Feld

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
                    self.entries[x,y] = {'rittername': row[5],
                                        'allyfarbe': row[8]}
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


# vim:set shiftwidth=4 expandtab smarttab:
