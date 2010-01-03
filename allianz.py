#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
import ausgabe

class Allianz:
    """Eine Klasse um Allianzdaten ein- und auszulesen.
    """

    def list(self):
        tabelle = ausgabe.Tabelle()
        tabelle.addColumn("a_id")
        tabelle.addColumn("Name")
        tabelle.addColumn("Tag")
        sql = "SELECT allinr, allicolor, alliname, alli"
        sql += " FROM allis"
        sql += " ORDER BY alliname"
        try:
            conn = rbdb.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            while row != None:
                line = [row[0]]
                zelle = '<a href="allianz/' + str(row[0]) + '">'
                zelle += '<div style="color:' + row[1] + ';">'
                zelle += row[2] + '</div></a>'
                line.append(zelle)
                line.append(row[3])
                tabelle.addLine(line)
                row = cursor.fetchone()
            print "Es sind", tabelle.length(), "Allianzen in der Datenbank"
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
        print '<title>Allianzliste</title>'
        print '</head>'
        print '<body>'

        allianz = Allianz()
        allianz.list()
    elif "id" in form:
        from armee import Armee
        a_id = form["id"].value

        print '<title>Allianz ' + a_id + '</title>'
        print '</head>'
        print '<body>'

        armee = Armee()
        allianz = Allianz()
        armeetabelle = armee.list_by_allianz(a_id)
        print "Anzahl Armeen:", armeetabelle.length()
        armeetabelle.show()

    print '</body></html>'


# vim:set shiftwidth=4 expandtab smarttab:
