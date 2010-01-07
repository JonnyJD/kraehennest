#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
from datetime import datetime, timedelta

import config
import ausgabe

def list_versions():
    tabelle = ausgabe.Tabelle()
    tabelle.addColumn("r_id")
    tabelle.addColumn("rittername")
    tabelle.addColumn("version")
    tabelle.addColumn("last_seen")
    sql = "SELECT r_id, rittername, version, last_seen"
    sql += " FROM versionen"
    sql += " left JOIN ritter ON r_id = ritternr"
    if config.is_tw():
        sql += " WHERE version like '%TW-Edition%'"
    elif not config.is_kraehe():
        sql += " WHERE 0" # liste garnichts
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
            string = ausgabe.datetime_delta_string(row[3])
            delta = datetime.today() - row[3]
            if delta > timedelta(hours=30):
                    zelle = '<div style="color:red">'
                    zelle += string + '</div>'
                    line.append(zelle)
            elif delta > timedelta(hours=6):
                    zelle = '<div style="color:orange">'
                    zelle += string + '</div>'
                    line.append(zelle)
            else:
                line.append(string)
            tabelle.addLine(line)
            row = cursor.fetchone()
        print "Es sind", tabelle.length(), "Benutzerreiche in der Datenbank"
        return tabelle.show()
    except rbdb.Error, e:
        util.print_html_error(e)
        return False



# Aufruf als Skript: Reich eintragen
if __name__ == '__main__':
    form = cgi.FieldStorage()

    if not config.is_admin():
        ausgabe.print_header("Unberechtigter Zugriff")
    elif "list" in form:
        if form["list"].value == "versionen":
            ausgabe.print_header("Versionsliste")
            list_versions()
        else:
            ausgabe.print_header("Administration")
    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
