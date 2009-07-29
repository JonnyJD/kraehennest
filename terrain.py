#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import rbdb
import util

class Terrain:
    def __init__(self):
        self.__entries = dict()
        self.__new_entries = []
        self.__conn = rbdb.connect()
        self.__cursor = self.__conn.cursor()

    def disconnect(self):
        self.__cursor.close()
        self.__conn.close()


    def __try_execute(self, sql):
        try:
            self.__cursor.execute(sql)
            return self.__cursor.rowcount
        except rbdb.Error, e:
            util.print_html_error(e)
            return 0

    def __try_execute_secondary(self, sql):
        try:
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            cursor.close()
            return self.__cursor.rowcount
        except rbdb.Error, e:
            util.print_html_error(e)
            return 0


    def fetch_data(self, level='N',
            xmin=None, xmax=None, ymin=None, ymax=None):
        self.level = level
        self.__crop(xmin, xmax, ymin, ymax)
        self.__get_border()
        self.__get_entries()


    def __crop(self, xmin, xmax, ymin, ymax):
        self.__crop_clause = ""
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
            self.__crop_clause = " AND " + " AND ".join(clauses)


    def __type(self, fields):
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


    def queue_entry(self, fields):
        if len(fields) >= 4:
            f = {"level": fields[0], "x": fields[1], "y": fields[2],
                    "terrain": fields[3], "typ": self.__type(fields)}
            if (    f["x"].isdigit() and f["y"].isdigit()
                    and f["terrain"].isalnum() and len(f["terrain"]) <= 4
                    and f["level"].isalnum() and len(f["level"]) <= 2):
                self.__new_entries.append(f)
                return True

        return False


    def __update(self, feld):
        sql = "UPDATE felder "
        sql += "SET terrain = '" + feld["terrain"] + "'"
        if feld["typ"] != None:
            sql += ", typ = " + feld["typ"]
        sql += " WHERE level = '" + feld["level"] + "' AND "
        sql += "x = " + feld["x"] + " AND y = " + feld["y"]
        return self.__try_execute_secondary(sql)


    def __check_old(self):
        """Gleicht die einzufuegenden Felder mit in der DB vorhandenen ab."""

        new = self.__new_entries
        num_updated = 0
        sql = "SELECT level, x, y, terrain, typ FROM felder WHERE "
        for f in new:
            sql += "(level = '" + f["level"] + "' AND "
            sql += "x = " + f["x"] + " AND y = " + f["y"] + ")"
            sql += " OR "
        self.__cursor.execute(sql.rstrip(" OR "))
        row = self.__cursor.fetchone()
        while row != None:
            i = 0
            while i < len(new):
                if (    new[i]["level"] == row[0] and
                        new[i]["x"] == str(row[1]) and
                        new[i]["y"] == str(row[2])      ):
                    if (    new[i]["terrain"] != row[3] or
                            (   new[i]["typ"] != None and
                                new[i]["typ"] != str(row[4])    )    ):
                        print new, "<br />"
                        print row, "<br />"
                        if self.__update(new[i]):
                            num_updated += 1
                    # jetzt in jedem Fall schon (voll) drin
                    del new[i]
                else:
                    i += 1
            row = self.__cursor.fetchone()
        return num_updated


    def __insert_type(self):
        sql = "INSERT INTO felder (x, y, level, terrain, typ) VALUES "
        new = self.__new_entries
        num = 0
        i = 0
        while i < len(new):
            if new[i]["typ"] != None:
                sql += "(" + new[i]["x"] + "," + new[i]["y"] + ",'"
                sql += new[i]["level"] + "','" + new[i]["terrain"] + "'),"
                del new[i]
                num += 1
            else:
                i += 1
        if num > 0:
            if self.__try_execute(sql.rstrip(',')):
                return self.__cursor.rowcount
        return 0

    def __insert(self):
        typenum = self.__insert_type()
        if len(self.__new_entries) > 0:
            sql = "INSERT INTO felder (x, y, level, terrain) VALUES "
            for new in self.__new_entries:
                sql += "(" + new["x"] + "," + new["y"] + ",'"
                sql += new["level"] + "','" + new["terrain"] + "'),"
            self.__new_entries = []
            if self.__try_execute(sql.rstrip(',')):
                return self.__cursor.rowcount + typenum
        return 0


    def exec_queue(self):
        update_count = self.__check_old()
        insert_count = self.__insert()
        return update_count, insert_count


    def _get_border(self):
        self.xmin, self.xmax, self.ymin, self.ymax = 0, 0, 0, 0
        sql = "SELECT MIN(X), MAX(x), MIN(y), MAX(y) FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.__crop_clause
        try:
            self.__cursor.execute(sql)
            row = self.__cursor.fetchone()
            if row[0] != None:
                self.xmin, self.xmax = row[0], row[1]
                self.ymin, self.ymax = row[2], row[3]
                return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


    def _get_entries(self):
        sql = "SELECT x, y, terrain FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.__crop_clause
        try:
            self.__cursor.execute(sql)
            row = self.__cursor.fetchone()
            while row != None:
                self.__entries[row[0],row[1]] = row[2]
                row = self.__cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


    def has(self, x, y):
        return (x,y) in self.__entries

    def get(self, x, y):
        return self.__entries[x,y]


# Aufruf als Skript: Landschaftsaktualisierung
if __name__ == '__main__':
    form = cgi.FieldStorage()
    print "Content-type: text/plain\n"

    if form.has_key("data"):
        terrain = Terrain()

        lines = form["data"].value.splitlines()
        for line in lines:
            fields = line.split()
            if not terrain.queue_entry(fields):
                print '"', line, '" enthielt Fehler <br />'
        updated, added = terrain.exec_queue()
        if (updated + added) > 0:
            print "Es wurden", updated, "Felder aktualisiert und",
            print added, "neu hinzugefuegt"
        else:
            print "Terrain ist schon bekannt."

    else:
        # Hier spaeter selbst ein Formular
        print 'Es wurden keine Landschaftsdaten gesendet.'



# vim:set shiftwidth=4 expandtab smarttab:
