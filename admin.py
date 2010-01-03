#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
from ausgabe import Tabelle

def list_versions():
    tabelle = Tabelle()
    tabelle.addColumn("r_id")
    tabelle.addColumn("rittername")
    tabelle.addColumn("version")
    tabelle.addColumn("last_seen")
    sql = "SELECT r_id, rittername, version, last_seen"
    sql += " FROM versionen"
    sql += " left JOIN ritter ON r_id = ritternr"
    sql += " ORDER BY last_seen DESC"
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        while row != None:
            line = [row[0]]
            if row[1] is None:
                zelle = '<a href="reich/' + str(row[0]) + '">?</a>'
            else:
                zelle = '<a href="reich/' + str(row[0]) + '">' + row[1] + '</a>'
            line.append(zelle)
            line.append(row[2])
            line.append(row[3])
            tabelle.addLine(line)
            row = cursor.fetchone()
        print "Es sind", tabelle.length(), "Benutzerreiche in der Datenbank"
        return tabelle.show()
    except rbdb.Error, e:
        util.print_html_error(e)
        return False



# Aufruf als Skript: Reich eintragen
if __name__ == '__main__':
    print 'Content-type: text/html; charset=utf-8\n'
    print '<html><head>'
    print '<link rel="stylesheet" type="text/css" href="../stylesheet">'

    form = cgi.FieldStorage()

    if "list" in form:
        if form["list"].value == "versionen":
            print '<title>Versionsliste</title>'
            print '</head>'
            print '<body>'
            list_versions()
            print '</body></html>'


# vim:set shiftwidth=4 expandtab smarttab:
