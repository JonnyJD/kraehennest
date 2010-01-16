#!/usr/bin/python
"""Administrative Aufgaben"""

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
from datetime import datetime, timedelta

import config
import ausgabe

def list_versions():
    """Listet fuer jeden Ritter die benutze Kraehenaugenversion und Zeit"""

    tabelle = ausgabe.Tabelle()
    if config.is_kraehe():
        tabelle.addColumn("Account")
    tabelle.addColumn("r_id")
    tabelle.addColumn("Rittername")
    tabelle.addColumn("Version")
    tabelle.addColumn("zuletzt gesehen")
    sql = "SELECT r_id, rittername, version, last_seen"
    if config.is_kraehe():
        sql += ", username"
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
            line = []
            if config.is_kraehe():
                line.append(row[4])
            line.append(row[0])
            if config.is_kraehe() and row[1] is None:
                zelle = '<a href="reich/' + str(row[0]) + '">?</a>'
            elif config.is_kraehe():
                zelle = '<a href="reich/' + str(row[0]) + '">' + row[1] + '</a>'
            else:
                zelle = row[1]
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
        tabelle.show()
        return True
    except rbdb.Error, e:
        util.print_html_error(e)
        return False

def list_too_many_armies():
    """Listet Ritter mit ueberzaehligen Armeen"""

    tabelle = ausgabe.Tabelle()
    tabelle.addColumn("Rittername")
    tabelle.addColumn("Armeen")
    sql = "SELECT ritternr, rittername, count(distinct h_id) as armeezahl"
    sql += " FROM ritter"
    sql += " JOIN armeen ON ritternr = r_id"
    sql += " GROUP BY ritternr, rittername"
    sql += " HAVING armeezahl > 4"
    sql += " ORDER BY ritternr"
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        while row != None:
            line = [ausgabe.link("/show/reich/" + str(row[0]), row[1])]
            line.append(row[2])
            tabelle.addLine(line)
            row = cursor.fetchone()
        print "Es haben", tabelle.length(), "Reiche mehr als 4 Armeen"
        tabelle.show()
        return True
    except rbdb.Error, e:
        util.print_html_error(e)
        return False

def list_dangling_armies():
    """Listet Armeen mit unbekanntem Ritter"""

    tabelle = ausgabe.Tabelle()
    tabelle.addColumn("Armee")
    tabelle.addColumn("r_id")
    tabelle.addColumn("Admin")
    sql = "SELECT h_id, name, r_id, max_dauer"
    sql += " FROM armeen"
    sql += " WHERE r_id NOT IN (SELECT distinct ritternr FROM ritter)"
    sql += " ORDER BY r_id"
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        while row != None:
            line = [row[1]]
            line.append(row[2])
            if row[3] is None: # kein Soeldner
                url = "/delete/armee/" + str(row[0])
                line.append(ausgabe.link(url, "[del]"))
            else:
                url = "/disown/armee/" + str(row[0])
                line.append(ausgabe.link(url, "[free]"))
            tabelle.addLine(line)
            row = cursor.fetchone()
        print "Es haben", tabelle.length(), "Armeen keine Ritter mehr"
        tabelle.show()
        return True
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
        elif form["list"].value == "delete":
            ausgabe.print_header("L&ouml;schliste")
            print '<div class="box">'
            list_too_many_armies()
            print '</div>'
            print '<div class="box">'
            list_dangling_armies()
            print '</div>'
        else:
            ausgabe.print_header("Administration")
    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
