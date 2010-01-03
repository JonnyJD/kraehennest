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


# Aufruf als Skript
if __name__ == '__main__':
    form = cgi.FieldStorage()

    if "list" in form:
        ausgabe.print_header("Allianzliste")

        allianz = Allianz()
        allianz.list()
    elif "id" in form:
        from reich import Reich
        from dorf import Dorf
        from armee import Armee

        a_id = form["id"].value

        ausgabe.print_header("Allianz " + a_id)

        print '<table>'
        reich = Reich()
        reichtabelle = reich.list_by_allianz(a_id)
        print '<tr><td><a href="#reiche">Reiche</a></td>'
        print '<td>' + str(reichtabelle.length()) + '</td></tr>'
        dorf = Dorf()
        dorftabelle = dorf.list_by_allianz(a_id)
        print '<tr><td><a href="#doerfer">D&ouml;rfer</a></td>'
        print '<td>' + str(dorftabelle.length()) + '</td></tr>'
        armee = Armee()
        armeetabelle = armee.list_by_allianz(a_id)
        print '<tr><td><a href="#armeen">Armeen</a></td>'
        print '<td>' + str(armeetabelle.length()) + '</td></tr>'
        print '</table>'

        print '<h2 id="reiche">Reiche</h2>'
        reichtabelle.show()
        print '<h2 id="doerfer">D&ouml;rfer</h2>'
        dorftabelle.show()
        print '<h2 id="armeen">Armeen</h2>'
        armeetabelle.show()

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
