#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
from feld import Feld

class Terrain(Feld):
    """Eine Klasse um Terraindaten ein- und auszulesen.
    
    Einlesen:
        Mit queue_entry(fields) werden die Felder einzeln uebergeben.
        Mit exec_queue() werden dann alle eingetragen, falls nicht vorhanden.
        Mit replace_uniform_area(level, x1, y1, x2, y2, terrain)
        und replace_line(level, x, y, terrain_list)
        koennen Terraindaten manuell eingetragen werden

    Auslesen:
        Mit set_add_cond() kann man eine weitere Bedingung vorgeben.
        Danach wird mit fetch_data([level[, xmin[, xmax[, ymin[, ymax]]]]])
        alles passende von der Datenbank geladen.
        Mit has(x,y) und get(x,y) kann man dann einzeln zugreifen.
    
    Beenden:
        Mit disconnect() kann die Datenbankverbindung beendet werden.
        Danach koennen nurnoch die bereits geladenen Daten geholt werden."""

    def __type(self, fields):
        """Findet den Untertyp (I,II,III) eines Feldes heraus."""

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
        return (entry["x"].isdigit() and entry["y"].isdigit()
                and entry["terrain"].isalnum() and len(entry["terrain"]) <= 5
                and entry["level"].isalnum() and len(entry["level"]) <= 2)


    def queue_entry(self, fields):
        """Nimmt ein Feld zum Eintragen erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind."""

        if len(fields) >= 4:
            f = {"level": fields[0], "x": fields[1], "y": fields[2],
                    "terrain": fields[3], "typ": self.__type(fields)}
            if self.__check_entry(f):
                self.new_entries.append(f)
                return True

        return False


    def __update(self, feld):
        sql = "UPDATE felder "
        sql += "SET terrain = '" + feld["terrain"] + "'"
        if feld["typ"] != None:
            sql += ", typ = " + feld["typ"]
        sql += " WHERE level = '" + feld["level"] + "' AND "
        sql += "x = " + feld["x"] + " AND y = " + feld["y"]
        return self.try_execute_secondary(sql)


    def __check_old(self):
        """Gleicht die einzufuegenden Felder mit in der DB vorhandenen ab.
        
        Identische Eintragungen werden aus der TODO-Liste entnommen
        und Aenderungen werden sofort ausgefuehrt."""

        new = self.new_entries
        num_updated = 0
        sql = "SELECT level, x, y, terrain, typ FROM felder WHERE "
        for f in new:
            sql += "(level = '" + f["level"] + "' AND "
            sql += "x = " + f["x"] + " AND y = " + f["y"] + ")"
            sql += " OR "
        self.cursor.execute(sql.rstrip(" OR "))
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
        """Fuegt einen Eintrag mit einer Untertypangabe zur Datenbank hinzu."""

        sql = "INSERT INTO felder (x, y, level, terrain, typ) VALUES "
        new = self.new_entries
        num = 0
        i = 0
        while i < len(new):
            if new[i]["typ"] != None:
                sql += "(" + new[i]["x"] + "," + new[i]["y"] + ",'"
                sql += new[i]["level"] + "','"
                sql += new[i]["terrain"] + "'," + new[i]["typ"] + "),"
                del new[i]
                num += 1
            else:
                i += 1
        if num > 0:
            if self.try_execute(sql.rstrip(',')):
                return self.cursor.rowcount
        return 0

    def __insert(self):
        """Fuegt alle in der TODO-Liste verbliebenen Eintraege in die DB ein.

        Es wird hier davon ausgegangen, dass diese Eintraege
        noch nicht in der Datenbank vorhanden sind."""

        typenum = self.__insert_type()
        if len(self.new_entries) > 0:
            sql = "INSERT INTO felder (x, y, level, terrain) VALUES "
            for new in self.new_entries:
                sql += "(" + new["x"] + "," + new["y"] + ",'"
                sql += new["level"] + "','" + new["terrain"] + "'),"
            self.new_entries = []
            if self.try_execute(sql.rstrip(',')):
                return self.cursor.rowcount + typenum
        return 0


    def exec_queue(self):
        """Die TODO-Liste wird abgearbeitet.

        Die Eintraege werden als Aktualisierung oder Anfuegung
        der Datenbank hinzugefuegt.
        Es wird geprueft ob Eintraege nicht schon in der Datenbank sind.
        Die Anzahl der aktualisierten und der neuen Eintraege
        wird zurueckgegeben."""

        update_count = self.__check_old()
        insert_count = self.__insert()
        return update_count, insert_count

    def replace_uniform_area(self, level, x1, y1, x2, y2, terrain):
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

        self.level = level
        self.crop(xmin, xmax, ymin, ymax)
        self.__get_border()
        self.__get_entries()


    def __get_border(self):
        """Findet die tatsaechlichen Grenzen der aktuellen Karte heraus."""

        self.xmin, self.xmax, self.ymin, self.ymax = 0, 0, 0, 0
        sql = "SELECT MIN(X), MAX(x), MIN(y), MAX(y) FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.crop_clause
        sql += self.add_cond
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            if row[0] != None:
                self.xmin, self.xmax = row[0], row[1]
                self.ymin, self.ymax = row[2], row[3]
                return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank."""

        sql = "SELECT x, y, terrain FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.crop_clause
        sql += self.add_cond
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            while row != None:
                self.entries[row[0],row[1]] = row[2]
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def process(self, data):
        lines = data.splitlines()
        if len(lines) > 0:
            for line in lines:
                fields = line.split()
                if not self.queue_entry(fields):
                    print '"', line, '" enthielt Fehler <br />'
            updated, added = self.exec_queue()
            if (updated + added) > 0:
                print "Es wurden", updated, "Felder aktualisiert und",
                print added, "neu hinzugefuegt.", "<br />"
            else:
                print "Terrain ist schon bekannt.", "<br />"
        else:
            print 'Es wurden keine Landschaftsdaten gesendet.', "<br />"

    def process_xml(self, node):
        self.process(node.getContent());


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
