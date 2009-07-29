#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import rbdb
import util

class Terrain:
    def __init__(self):
        self.__entries = dict()
        self.__new_entries = []         # 
    
    def __connect(self):
        self.__conn = rbdb.connect()
        self.__cursor = self.__conn.cursor()

    def __disconnect(self):
        self.__cursor.close()
        self.__conn.close()

    def fetch_data(self, level='N', xmin=None, xmax=None, ymin=None, ymax=None):
        self.level = level
        self.__crop(xmin, xmax, ymin, ymax)
        self.__connect()
        self.__get_border()
        self.__get_entries()
        self.__disconnect()

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

    def start_query(self):
        self.__query = "REPLACE INTO felder (x, y, level, terrain) VALUES "
        self.__query_items = 0;

    def _type(self, fields):
        if len(fields) >= 5:
            type = fields[len(fields)-1]
            print type, '<br />'
            if type == "IV":
                typenum = "4"
            elif type == "IIII":
                typenum = "4"
            elif type == "III":
                typenum = "3"
            elif type == "II":
                typenum = "2"
            elif type == "I":
                typenum = "1"
            else:
                typenum = "1"
            try:
                conn = rbdb.connect()
                cursor2 = conn.cursor()
                sql = "REPLACE INTO felder (x, y, level, terrain, typ) VALUES "
                sql += "(" + fields[1] + "," + fields[2] + ",'"
                sql += fields[0] + "','" + fields[3] + "'," + typenum + ")"
                #print sql, "<br />"
                cursor2.execute(sql)
                cursor2.close()
                conn.close()
                return True
            except rbdb.Error, e:
                util.print_error(e)
                return False
        else:
            return False

    def add_to_query(self, fields):
        if len(self.__query) == 0:
            print 'Noch keine Query gestartet'
            return False

        if len(fields) >= 4:
            level = fields[0]
            x = fields[1]
            y = fields[2]
            terrain = fields[3]
            if (    x.isdigit() and y.isdigit()
                    and terrain.isalnum() and len(terrain) <= 4
                    and level.isalnum() and len(level) <= 2):
                self.__new_entries.append(fields)
                #self.__type(fields) # Untertyp eintragen
                self.__query += "(" + x + "," + y + ",'"
                self.__query += level + "','" + terrain + "'),"
                self.__query_items += 1
                return True

        return False

    def exec_query(self):
        try:
            self.__connect()
            #print self.__query.rstrip(','), "<br />"
            self.__cursor.execute(self.__query.rstrip(','))
            self.__disconnect()
            number = self.__query_items
            # reset query
            self.__query = 0;
            self.__query_items = 0;
            return number
        except rbdb.Error, e:
            util.print_error(e)
            return 0

    def _get_border(self):
        sql = "SELECT MIN(X), MAX(x), MIN(y), MAX(y) FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.__crop_clause
        self.__cursor.execute(sql)
        row = self.__cursor.fetchone()
        if row[0] != None:
            self.xmin, self.xmax = row[0], row[1]
            self.ymin, self.ymax = row[2], row[3]
        else:
            self.xmin, self.xmax, self.ymin, self.ymax = 0, 0, 0, 0

    def _get_entries(self):
        sql = "SELECT x, y, terrain FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.__crop_clause
        self.__cursor.execute(sql)
        row = self.__cursor.fetchone()
        while row != None:
            self.__entries[row[0],row[1]] = row[2]
            row = self.__cursor.fetchone()

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
        terrain.start_query()

        lines = form["data"].value.splitlines()
        correct = 0
        for line in lines:
            fields = line.split()
            if terrain.add_to_query(fields):
                correct += 1
            else:
                print '"', line, '" enthielt Fehler <br />'
        print terrain.exec_query(), 'Felder wurden eingetragen'

    else:
        # Hier spaeter selbst ein Formular
        print 'Es wurden keine Landschaftsdaten gesendet.'



# vim:set shiftwidth=4 expandtab smarttab:
