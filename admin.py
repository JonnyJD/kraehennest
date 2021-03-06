#!/usr/bin/env python
"""Administrative Aufgaben"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import rbdb
import util
from datetime import datetime, timedelta

import ausgabe

def list_versions(ver_type=None):
    """Listet fuer jeden Ritter die benutze Kraehenaugenversion und Zeit"""

    if config.is_kraehe():
        if ver_type != None:
            vers = ""
            print ausgabe.link("../versionen", "[alle]")
        else:
            vers = "versionen/"
            print "[alle]"
        if ver_type == None or ver_type.lower() != "ksk":
            print ausgabe.link(vers+"KSK", "[KSK]")
        else:
            print "[KSK]"
        if ver_type == None or ver_type.lower() != "tw":
            print ausgabe.link(vers+"TW", "[TW]")
        else:
            print "[TW]"
        if ver_type == None or ver_type.lower() != "brg":
            print ausgabe.link(vers+"BRG", "[BRG]")
        else:
            print "[BRG]"
        if ver_type == None or ver_type.lower() != "dr":
            print ausgabe.link(vers+"DR", "[DR]")
        else:
            print "[DR]"
        if ver_type == None or ver_type.lower() != "p":
            print ausgabe.link(vers+"P", "[P]")
        else:
            print "[P]"
        if ver_type == None or ver_type.lower() != "ext":
            print ausgabe.link(vers+"EXT", "[EXT]")
        else:
            print "[EXT]"
        print "<br /><br />"
    tabelle = ausgabe.Tabelle()
    tabelle.addColumn("Account")
    tabelle.addColumn("r_id")
    tabelle.addColumn("Rittername")
    tabelle.addColumn("Version")
    tabelle.addColumn("zuletzt gesehen")
    tabelle.addColumn("letzter Zug")
    sql = "SELECT r_id, rittername, allicolor, version, last_seen"
    sql += ", username, letzterzug"
    sql += " FROM versionen"
    sql += " left JOIN ritter ON r_id = ritternr"
    sql += " left JOIN allis ON ritter.alli = allinr"
    if ver_type:
        if ver_type.lower() == "ksk":
            sql += " WHERE version not like '%Edition%'"
        elif ver_type.lower() == "tw":
            sql += " WHERE version like '%TW-Edition%'"
            if config.is_tw():
                sql += " AND username is not NULL"
        elif ver_type.lower() == "brg":
            sql += " WHERE version like '%BRG-Edition%'"
        elif ver_type.lower() == "dr":
            sql += " WHERE version like '%DR-Edition%'"
        elif ver_type.lower() == "p":
            sql += " WHERE version like '%P-Edition%'"
        elif ver_type.lower() == "ext":
            sql += " WHERE version like '%xtern%Edition%'"
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
            row = ausgabe.escape_row(row)
            line.append(row[5]) # username
            line.append(row[0]) # r_id
            # Rittername
            if config.is_kraehe():
                if ver_type != None:
                    vers = "../"
                else:
                    vers = ""
                if row[1] is None:
                    zelle = ausgabe.link("%sreich/%d" % (vers, row[0]), "?")
                else:
                    zelle = ausgabe.link("%sreich/%d" % (vers, row[0]),
                                                        row[1], row[2])
            elif row[1] is None:
                zelle = "?"
            else:
                zelle = row[1]
            line.append(zelle)
            line.append(row[3]) # Version des Auges
            # zuletzt gesehen
            zelle = ausgabe.datetime_delta_color_string(row[4],
                    timedelta(hours=config.stunden_deaktivierung_2),
                    timedelta(days=config.tage_deaktivierung_3))
            line.append(zelle)
            # letzter Zug
            zelle = ausgabe.date_delta_color_string(row[6],
                    timedelta(hours=config.stunden_deaktivierung_2),
                    timedelta(days=config.tage_deaktivierung_3))
            line.append(zelle)
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
            row = ausgabe.escape_row(row)
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
    """Listet Armeen mit unbekanntem oder aufgeloestem Ritter"""

    tabelle = ausgabe.Tabelle()
    tabelle.addColumn("Armee")
    tabelle.addColumn("r_id")
    tabelle.addColumn("Admin")
    sql = "SELECT h_id, name, r_id, max_dauer, top10"
    sql += " FROM armeen"
    sql += " LEFT JOIN ritter ON r_id=ritternr"
    sql += " WHERE r_id is not NULL AND r_id NOT IN (113,143,160,172,174)"
    sql += " AND (top10 is NULL OR top10=0)"
    sql += " ORDER BY r_id"
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        while row != None:
            row = ausgabe.escape_row(row)
            line = [row[1]]
            if row[4] == 0:
                line.append(ausgabe.link("/show/reich/"+str(row[2]), row[2]))
            else:
                line.append(row[2])
            if row[4] is None and row[3] is None: # kein Soeldner
                url = "/delete/armee/" + str(row[0])
                line.append(ausgabe.link(url, "[del]"))
            elif row[4] is None:
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
#if __name__ == '__main__':
if True:
    form = cgi.FieldStorage()

    if not config.is_admin():
        ausgabe.print_header("Unberechtigter Zugriff")
    elif "list" in form:
        if form["list"].value == "versionen":
            if "type" in form:
                ver_type = form["type"].value 
                ausgabe.print_header("Versionsliste: " + ver_type)
                list_versions(ver_type)
            else:
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
