#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import rbdb
import util

class Terrain:
    def __init__(self):
        self.entries = dict()
    
    def _connect(self):
        self.conn = rbdb.connect()
        self.cursor = self.conn.cursor()

    def _disconnect(self):
        self.cursor.close()
        self.conn.close()

    def fetch_data(self, level='N', xmin=None, xmax=None, ymin=None, ymax=None):
        self.level = level
        self._crop(xmin, xmax, ymin, ymax)
        self._connect()
        self._get_border()
        self._get_entries()
        self._disconnect()

    def _crop(self, xmin, xmax, ymin, ymax):
        self.cropclause = ""
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
            self.cropclause = " AND " + " AND ".join(clauses)

    def start_query(self):
        self.query = "REPLACE INTO felder (x, y, level, terrain) VALUES "
        self.queryitems = 0;

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
        if len(self.query) == 0:
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
                #self._type(fields) # Untertyp eintragen
                self.query += "(" + x + "," + y + ",'"
                self.query += level + "','" + terrain + "'),"
                self.queryitems += 1
                return True

        return False

    def exec_query(self):
        try:
            self._connect()
            #print self.query.rstrip(','), "<br />"
            self.cursor.execute(self.query.rstrip(','))
            self._disconnect()
            number = self.queryitems
            # reset query
            self.query = 0;
            self.queryitems = 0;
            return number
        except rbdb.Error, e:
            util.print_error(e)
            return 0

    def _get_border(self):
        sql = "SELECT MIN(X), MAX(x), MIN(y), MAX(y) FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.cropclause
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        if row[0] != None:
            self.xmin, self.xmax = row[0], row[1]
            self.ymin, self.ymax = row[2], row[3]
        else:
            self.xmin, self.xmax, self.ymin, self.ymax = 0, 0, 0, 0

    def _get_entries(self):
        sql = "SELECT x, y, terrain FROM felder"
        sql += " WHERE level='" + self.level + "'"
        sql += self.cropclause
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        while row != None:
            self.entries[row[0],row[1]] = row[2]
            row = self.cursor.fetchone()

    def has(self, x, y):
        return (x,y) in self.entries

    def get(self, x, y):
        return self.entries[x,y]


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
