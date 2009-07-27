#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import rbdb
import util

print "Content-type: text/plain\n"

def add_to_query(fields):
    if len(fields) >= 4:
        level = fields[0]
        x = fields[1]
        y = fields[2]
        terrain = fields[3]
        if not x.isdigit() or not y.isdigit() or not terrain.isdigit():
            return None
        elif not level.isalnum() or len(level) >= 2:
            return None
        else:
            return "(" + x + "," + y + ",'" + level + "'," + terrain + "),"
    else:
        return None

form = cgi.FieldStorage()
if form.has_key("data"):
    conn = rbdb.connect()
    cursor = conn.cursor()
    sql = "REPLACE INTO felder (x, y, level, terrain) VALUES "

    lines = form["data"].value.splitlines()
    correct = 0
    for line in lines:
        fields = line.split()
        current = add_to_query(fields)
        if current != None:
            sql += current
            correct += 1
        else:
            print '"', line, '" enthielt Fehler <br />'
    sql = sql.rstrip(',')
    try:
        cursor.execute(sql)
        print correct, 'Felder wurden eingetragen'
    except rbdb.Error, e:
        util.print_error(e)

else:
    print 'Es wurden keine Landschaftsdaten gesendet.'


cursor.close()
conn.close()

# vim:set shiftwidth=4 expandtab smarttab:
