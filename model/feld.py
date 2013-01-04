#!/usr/bin/env python
"""Die Grundstruktur von Klassen die Daten zu einem bestimmten Feld bearbeiten.
"""

import rbdb
import util

class Feld:
    """Eine abstrakte Klasse um Felddaten ein- und auszulesen.  
    """

    def __init__(self, x=None, y=None, level="N"):
        """Stellt eine Verbindung zur Datenbank her und initialisiert

        bzw. erstellt eine Feldinstanz..
        @type x: C{IntType}
        @type y: C{IntType}
        @type level: C{StringType}
        """

        if x is None:
            self.entries = dict()
            self.new_entries = []
            self.add_cond = ""
            self.conn = rbdb.connect()
            self.cursor = self.conn.cursor()
            self.crop_clause = ""
            self.cond_clause = ""
        else:
            sql = "SELECT terrain, typ"
            sql += " FROM felder"
            sql += " WHERE level = %s AND x = %s AND y = %s"
            row = util.get_sql_row(sql, (level, x, y))
            if row is None:
                raise KeyError(level, x, y)
            else:
                self.terrain = row[0]
                """Art des Terrains
                @type: C{IntType}
                """
                self.typ = row[1]
                """Untertyp des Terrains
                @type: C{IntType}
                """


    def disconnect(self):
        """Beende die Verbindung zur Datenbank
        """
        self.cursor.close()
        self.conn.close()

    def try_execute_safe(self, sql, args):
        """Fuehrt eine SQL-Query aus

        @param sql: Query mit Platzhaltern
        @param args: Tupel mit Variablen
        @return: Anzahl der Aenderungen
        @rtype: C{IntType}
        """
        return util.try_execute_safe(self.cursor, sql, args)

    def try_executemany_safe(self, sql, arglist):
        """Fuehrt eine SQL-Query mit mehrmals aus

        @param sql: Query mit Platzhaltern
        @param arglist: Liste von Tupeln mit Variablen
        @return: Anzahl der Aenderungen
        @rtype: C{IntType}
        """
        return util.try_executemany_safe(self.cursor, sql, arglist[:])

    def try_execute_safe_secondary(self, sql, args):
        """Fuehrt eine SQL-Query mit einem zweiten Cursor aus

        @param sql: Query mit Platzhaltern
        @param args: Tupel mit Variablen
        @return: Anzahl der Aenderungen
        @rtype: C{IntType}
        """
        cursor = self.conn.cursor()
        affectedrows = util.try_execute_safe(cursor, sql, args)
        cursor.close()
        return affectedrows


    def queue_entry(self, fields):
        """Nimmt ein Feld zum Eintragen erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind.
        @rtype: C{BooleanType}
        """
        return True


    def exec_queue(self):
        """Die TODO-Liste wird abgearbeitet.

        Die Eintraege werden als Aktualisierung oder Anfuegung
        der Datenbank hinzugefuegt.
        Es wird geprueft ob Eintraege nicht schon in der Datenbank sind.
        @return: Anzahl der aktualisierten und der neuen Eintraege
        @rtype: C{IntType}
        """

        return 0


    def set_add_cond(self, sql):
        """Definiert eine zusaetzliche Bedingung fuer die Felder."""

        if sql != None:
            self.add_cond = " AND " + sql
        else:
            self.add_cond = ""


    def replace_cond(self, sql):
        """Ersetzt die Bedingung fuer die Felder."""

        if sql != None:
            self.cond_clause = " AND " + sql


    def fetch_data(self, level='N',
            xmin=None, xmax=None, ymin=None, ymax=None):
        """Liest die Terraindaten von der Datenbank aus."""

        pass
        #self.level = level
        #self.crop(xmin, xmax, ymin, ymax)
        #self.__get_border()
        #self.__get_entries()


    def crop(self, xmin, xmax, ymin, ymax):
        """Erstellt die SQL-Bedingung mit der der Bereich festgelegt wird."""

        try:
            clauses = []
            if xmin != None:
                clauses.append(" x >= " + str(int(xmin)))
            if xmax != None:
                clauses.append(" x <= " + str(int(xmax)))
            if ymin != None:
                clauses.append(" y >= " + str(int(ymin)))
            if ymax != None:
                clauses.append(" y <= " + str(int(ymax)))
            if len(clauses) > 0:
                self.crop_clause = " AND " + " AND ".join(clauses)
        except ValueError:
            print "Die angegebenene Grenzen sind ungueltig <br />"

    def get_border(self):
        """Findet die tatsaechlichen Grenzen der aktuellen Karte heraus.
        
        @rtype: C{BooleanType}
        """

        self.xmin, self.xmax, self.ymin, self.ymax = 0, 0, 0, 0
        sql = "SELECT MIN(X), MAX(x), MIN(y), MAX(y) FROM "
        sql += self.table_name
        sql += " WHERE level='" + self.level + "'"
        sql += self.crop_clause
        sql += self.cond_clause
        sql += self.add_cond
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            if row[0] != None:
                self.xmin, self.xmax = row[0], row[1]
                self.ymin, self.ymax = row[2], row[3]
                return True
            else:
                return False
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank.
        
        @rtype: C{BooleanType}
        """
        return True


    def has(self, x, y):
        """Fragt ab ob auf diesem Feld ein Eintrag existiert

        @rtype: C{BooleanType}
        """
        return (x,y) in self.entries

    def get(self, x, y):
        """Gibt den Eintrag auf diesem Feld zurueck

        @rtype: meist C{Dict}
        """
        if self.has(x, y):
            self.entry = self.entries[x,y]
        else:
            self.entry = None
        return self.entry


# vim:set shiftwidth=4 expandtab smarttab:
