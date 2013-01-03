#!/usr/bin/env python
"""Modul um Terraindaten einzulesen und auszugeben"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import rbdb
import util
from model import Feld

class Terrain(Feld):
    """Eine Klasse um Terraindaten ein- und auszulesen.  
    """

    def __init__(self):
        """Verbindung mit der Datenbank und Initialisierung
        """
        Feld.__init__(self)
        self.table_name = "felder"

    def __type(self, fields):
        """Findet den Untertyp (I,II,III) eines Feldes heraus.
        
        @rtype: C{IntType}
        """

        if len(fields) >= 5:
            type = fields[len(fields)-1]
            if type == "IV":
                return "4"
            elif type == "IIII":
                return "4"
            elif type == "III":
                return "3"
            elif type == "II":
                return "2"
            elif type == "I":
                return "1"
            else:
                return "1"
        else:
            return None

    def __check_entry(self, entry):
        """Prueft auf Korrektheit der Daten

        @rtype: C{BooleanType}
        """
        return (entry["x"].isdigit() and entry["y"].isdigit()
                and entry["terrain"].isalnum() and len(entry["terrain"]) <= 5
                and entry["level"].isalnum() and len(entry["level"]) <= 2)


    def queue_entry(self, fields):
        """Nimmt ein Feld zum Eintragen erstmal in einer TODO-Liste auf.
        
        @return: Ob die Daten syntaktisch korrekt sind
        @rtype: C{BooleanType}
        """

        if len(fields) >= 4:
            f = {"level": fields[0], "x": fields[1], "y": fields[2],
                    "terrain": fields[3], "typ": self.__type(fields)}
            if self.__check_entry(f):
                self.new_entries.append(f)
                return True
            else:
                return False
        else:
            return False


    def __update(self, feld):
        """Aktualisiert die Datenbank mit den Feldern

        @return: aktualisierte Eintraege
        @rtype: C{IntType}
        """

        sql = "UPDATE felder SET terrain = %s"
        args = feld["terrain"],
        if feld["typ"] != None:
            sql += ", typ = %s"
            args += feld["typ"],
        sql += " WHERE level = %s AND x = %s AND y = %s"
        args += feld["level"], feld["x"], feld["y"]
        return self.try_execute_safe_secondary(sql, args)


    def __check_old(self):
        """Gleicht die einzufuegenden Felder mit in der DB vorhandenen ab.
        
        Identische Eintragungen werden aus der TODO-Liste entnommen
        und Aenderungen werden sofort ausgefuehrt.
        @return: Aktualisierungen
        @rtype: C{IntType}
        """

        new = self.new_entries
        num_updated = 0
        sql = "SELECT level, x, y, terrain, typ FROM felder WHERE "
        sqllist = []
        args = ()
        for f in new:
            sqllist.append("(level = %s AND x = %s AND y = %s)")
            args += f["level"], f["x"], f["y"]
        sql += " OR ".join(sqllist)
        self.try_execute_safe(sql, args)
        row = self.cursor.fetchone()
        while row != None:
            i = 0
            while i < len(new):
                if (    new[i]["level"] == row[0] and
                        new[i]["x"] == str(row[1]) and
                        new[i]["y"] == str(row[2])      ):
                    if (    new[i]["terrain"] != row[3] or
                            (   new[i]["typ"] != None and
                                new[i]["typ"] != str(row[4])    )    ):
                        if self.__update(new[i]):
                            num_updated += 1
                    # jetzt in jedem Fall schon (voll) drin
                    del new[i]
                else:
                    i += 1
            row = self.cursor.fetchone()
        return num_updated


    def __insert_type(self):
        """Fuegt einen Eintrag mit einer Untertypangabe zur Datenbank hinzu.
        
        @return: Anzahl Inserts
        @rtype: C{IntType}
        """

        sql = "INSERT INTO felder (x, y, level, terrain, typ)"
        sql += " VALUES (%s, %s, %s, %s, %s)"
        arglist = []
        new = self.new_entries
        i = 0
        while i < len(new):
            if new[i]["typ"] != None:
                args = new[i]["x"], new[i]["y"], new[i]["level"]
                args += new[i]["terrain"], new[i]["typ"]
                arglist.append(args)
                del new[i]
            else:
                i += 1
        if len(arglist) > 0:
            return self.try_executemany_safe(sql, arglist)
        else:
            return 0

    def __insert(self):
        """Fuegt alle in der TODO-Liste verbliebenen Eintraege in die DB ein.

        Es wird hier davon ausgegangen, dass diese Eintraege
        noch nicht in der Datenbank vorhanden sind.
        @return: Anzahl Inserts
        @rtype: C{IntType}
        """

        typenum = self.__insert_type()
        if len(self.new_entries) > 0:
            sql = "INSERT INTO felder (x, y, level, terrain)"
            sql += " VALUES (%s, %s, %s, %s)"
            arglist = []
            for new in self.new_entries:
                arglist += [(new["x"], new["y"], new["level"], new["terrain"])]
            self.new_entries = []
            return typenum + self.try_executemany_safe(sql, arglist)
        else:
            return typenum


    def exec_queue(self):
        """Die TODO-Liste wird abgearbeitet.

        Die Eintraege werden als Aktualisierung oder Anfuegung
        der Datenbank hinzugefuegt.
        Es wird geprueft ob Eintraege nicht schon in der Datenbank sind.
        @return: Anzahl der aktualisierten und der neuen Eintraege
        @rtype: C{IntType}, C{IntType}
        """

        update_count = self.__check_old()
        insert_count = self.__insert()
        return update_count, insert_count

    def replace_uniform_area(self, level, x1, y1, x2, y2, terrain):
        """Ersetzt einen rechteckigen Bereich der Karte

        Gedacht zur interaktiven/manuellen Nutzung
        @param level: Das Level
        @param x1: linke Grenze
        @param y1: obere Grenze
        @param x2: rechte Grenze
        @param y2: untere Grenze
        @param terrain: Zu schreibende Terrainart
        @type terrain: C{IntType} oder C{StringType}
        """

        for x in range(x1,x2+1):
            for y in range(y1,y2+1):
                f = {"level": level, "x": str(x), "y": str(y),
                        "terrain": str(terrain), "typ": None}
                if self.__check_entry(f):
                    self.new_entries.append(f)
                else:
                    print "Problem mit", f
        updated, inserted = self.exec_queue()
        print updated, "aktualisiert", inserted, "eingefuegt"

    def replace_line(self, level, x, y, terrain_list):
        """Ersetzt einen (Teil)Zeile der Karte

        Gedacht zur interaktiven/manuellen Nutzung
        @param terrain_list: Zu schreibende Terrainarten
        @type terrain_list: C{List}: C{IntType}/C{StringType}
        """
        for i in range(0,len(terrain_list)):
            f = {"level": level, "x": str(x), "y": str(y),
                    "terrain": str(terrain_list[i]), "typ": None}
            if self.__check_entry(f):
                self.new_entries.append(f)
            else:
                print "Problem mit", f
            x += 1
        updated, inserted = self.exec_queue()
        print updated, "aktualisiert", inserted, "eingefuegt"


    def fetch_data(self, level='N',
            xmin=None, xmax=None, ymin=None, ymax=None):
        """Liest die Terraindaten von der Datenbank aus."""

        if level.isalnum() and len(level) <= 2:
            self.level = level
            self.crop(xmin, xmax, ymin, ymax)
            self.get_border()
            self.__get_entries()
        else:
            print "FEHLER: Level '" + level + "' ist ung&uuml;ltig"

    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank.
        
        @return: Erfolgsstatus
        @rtype: C{BooleanType}
        """

        sql = "SELECT x, y, terrain, typ, info FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.crop_clause
        sql += self.add_cond
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            while row != None:
                entry = dict()
                entry["terrain"] = row[2]
                entry["typ"] = row[3]
                if row[4] and row[4].find("{{{abgang}}}") >= 0:
                    entry["abgang"] = True
                if row[4] and row[4].find("{{{aufgang}}}") >= 0:
                    entry["aufgang"] = True
                if row[4] and row[4].find("{{{quest}}}") >= 0:
                    entry["quest"] = True
                if row[4] and row[4].find("{{{ziel}}}") >= 0:
                    entry["ziel"] = True
                self.entries[row[0],row[1]] = entry
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def process(self, data):
        """Verarbeitet Landschaftsdaten als Text
        
        @param data: Felddaten
        @type data: C{StringType}
        """

        lines = data.splitlines()
        if len(lines) > 0:
            for line in lines:
                fields = line.split()
                if not self.queue_entry(fields):
                    print '"', line, '" enthielt Fehler <br />'
            updated, added = self.exec_queue()
            if (updated + added) > 0:
                print "Es wurden", updated, "Felder aktualisiert und",
                print added, "neu hinzugef&uuml;gt.", "<br />"
            else:
                print "Terrain ist schon bekannt.", "<br />"
        else:
            print 'Es wurden keine Landschaftsdaten gesendet.', "<br />"

    def process_xml(self, node):
        """Verarbeitet Landschaftsdaten als XML

        @param node: Landschaftsdaten
        @type node: XML Knoten
        """

        felder = node.xpathEval('feld')
        if len(felder) > 0:
            for feld in felder:
                fields = [feld.prop('level'), feld.prop('x'), feld.prop('y')]
                fields.append(feld.xpathEval('terrain')[0].getContent())
                names = feld.xpathEval('feldname')
                if len(names) > 0:
                    fields.extend(names[0].getContent().split())
                if not self.queue_entry(fields):
                    util.print_xml(feld)
                    print "enthielt Fehler <br />"
            updated, added = self.exec_queue()
            if (updated + added) > 0:
                print "Es wurden", updated, "Felder aktualisiert und",
                print added, "neu hinzugef&uuml;gt.", "<br />"
            else:
                print "Terrain ist schon bekannt.", "<br />"
        else:
            print 'Es wurden keine Landschaftsdaten gesendet.', "<br />"


# Aufruf als Skript: Landschaftsaktualisierung
if __name__ == '__main__':
    form = cgi.FieldStorage()
    print "Content-type: text/plain\n"

    util.track_client_version(form)

    if form.has_key("data"):
        terrain = Terrain()
        terrain.process(form["data"].value)
    else:
        terrain = Terrain()
        terrain.process("")


# vim:set shiftwidth=4 expandtab smarttab:
