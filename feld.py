#!/usr/bin/python

import rbdb
import util

class Feld:
    """Eine abstrakte Klasse um Felddaten ein- und auszulesen.
    
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

    def __init__(self):
        self.entries = dict()
        self.new_entries = []
        self.add_cond = ""
        self.__conn = rbdb.connect()
        self.cursor = self.__conn.cursor()

    def disconnect(self):
        self.cursor.close()
        self.__conn.close()

    def try_execute_safe(self, sql, args):
        return util.try_execute_safe(self.cursor, sql, args)

    def try_executemany_safe(self, sql, arglist):
        return util.try_executemany_safe(self.cursor, sql, arglist[:])

    def try_execute_safe_secondary(self, sql, args):
        cursor = self.__conn.cursor()
        affectedrows = util.try_execute_safe(cursor, sql, args)
        cursor.close()
        return affectedrows


    def queue_entry(self, fields):
        """Nimmt ein Feld zum Eintragen erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind."""

        return True


    def exec_queue(self):
        """Die TODO-Liste wird abgearbeitet.

        Die Eintraege werden als Aktualisierung oder Anfuegung
        der Datenbank hinzugefuegt.
        Es wird geprueft ob Eintraege nicht schon in der Datenbank sind.
        Die Anzahl der aktualisierten und der neuen Eintraege
        wird zurueckgegeben."""

        return 0


    def set_add_cond(self, sql):
        """Definiert eine zusaetzliche Bedingung fuer die Felder."""

        if sql != None:
            self.add_cond = " AND " + sql
        else:
            self.add_cond = ""


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

        self.crop_clause = ""
        clauses = []
        if xmin != None:
            clauses.append(" x >= " + str(xmin))
        if xmax != None:
            clauses.append(" x <= " + str(xmax))
        if ymin != None:
            clauses.append(" y >= " + str(ymin))
        if ymax != None:
            clauses.append(" y <= " + str(ymax))
        if len(clauses) > 0:
            self.crop_clause = " AND " + " AND ".join(clauses)


    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank."""

        return True


    def has(self, x, y):
        return (x,y) in self.entries

    def get(self, x, y):
        self.entry = self.entries[x,y]
        return self.entry


# vim:set shiftwidth=4 expandtab smarttab:
