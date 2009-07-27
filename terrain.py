#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import rbdb
import util

print "Content-type: text/plain\n"

def add_to_query(sql, fields):
    if len(fields) >= 4:
        level = fields[0]
        x = fields[1]
        y = fields[2]
        terrain = fields[3]
        sql += "(" + x + "," + y + ",'" + level + "'," + terrain + "),"
    return sql

form = cgi.FieldStorage()
if form.has_key("data"):
    conn = rbdb.connect()
    cursor = conn.cursor()
    sql = "REPLACE INTO felder (x, y, level, terrain) VALUES "

    lines = form["data"].value.splitlines()
    for line in lines:
        fields = line.split()
        sql = add_to_query(sql, fields)
    sql = sql.rstrip(',')
    try:
        cursor.execute(sql)
        print len(lines), 'Felder wurden eingetragen'
    except rbdb.Error, e:
        util.print_error(e)

else:
    print 'Es wurden keine Landschaftsdaten gesendet.'


cursor.close()
conn.close()

# vim:set shiftwidth=4 expandtab smarttab:
