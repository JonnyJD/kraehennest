#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import rbdb
import util
import ausgabe

def print_link(a_id, name=None, color=None):
    if name is None or color is None:
        sql = "SELECT alliname, color FROM allis WHERE allinr = %s"
        row = util.get_sql_row(sql, a_id)
        if row is None:
            raise KeyError(a_id)
        else:
            name = row[0]
            color = row[1]
    print '<a href="' + ausgabe.prefix + '/show/allianz/' + str(a_id) + '">'
    print '<div style="color:' + color + ';">' + name + '</div>'
    print '</a>'

class Allianz:
    """Eine Klasse um Allianzdaten ein- und auszulesen.
    """

    def get_name(self, a_id):
        sql = "SELECT alliname FROM allis WHERE allinr = %s"
        row = util.get_sql_row(sql, a_id)
        if row:
            return row[0]
        else:
            return "[unbekannte Allianz]"

    def list(self):
        tabelle = ausgabe.Tabelle()
        tabelle.addColumn("a_id")
        tabelle.addColumn("Name")
        tabelle.addColumn("Tag")
        tabelle.addColumn("Mitglieder")
        tabelle.addColumn("D&ouml;rfer")
        tabelle.addColumn("Armeen")
        sql = "SELECT allinr, allicolor, alliname, allis.alli"
        sql += ", count(distinct ritter.ritternr)"
        sql += ", count(distinct dorf.koords)"
        sql += ", count(distinct h_id)"
        sql += " FROM allis"
        sql += " LEFT JOIN ritter ON allinr = ritter.alli"
        sql += " LEFT JOIN dorf ON ritter.ritternr = dorf.ritternr"
        sql += " LEFT JOIN armeen ON ritter.ritternr = r_id"
        sql += " GROUP BY allinr, allicolor, alliname, allis.alli"
        sql += " ORDER BY alliname"
        try:
            conn = rbdb.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            while row != None:
                line = []
                if row[4] > 0: # positive Mitgliederzahl
                    line.append(row[0])
                    zelle = '<a href="allianz/' + str(row[0]) + '">'
                    zelle += '<div style="color:' + row[1] + ';">'
                    zelle += row[2] + '</div></a>'
                    line.append(zelle)
                    line.append(row[3])
                else:
                    zelle = '<div style="color:#666666;">'
                    zelle += str(row[0]) + '</div>'
                    line.append(zelle)
                    zelle = '<div style="color:#666666;">'
                    zelle += row[2] + '</div>'
                    line.append(zelle)
                    zelle = '<div style="color:#666666;">'
                    zelle += row[3] + '</div>'
                    line.append(zelle)
                for i in range(4,7):
                    if row[i] > 0:
                        line.append(row[i])
                    else:
                        line.append("")
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
        allianz = Allianz()
        name = allianz.get_name(a_id)

        ausgabe.print_header("Allianz: " + name)

        print '<table>'
        reich = Reich()
        reichtabelle = reich.list_by_allianz(a_id)
        print '<tr><td><a href="#reiche">Mitglieder</a></td>'
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
