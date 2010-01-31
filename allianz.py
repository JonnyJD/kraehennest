#!/usr/bin/env python
"""Ein Modul um Allianzdaten auszugeben und zu listen."""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import rbdb
import util
import ausgabe


def link(a_id, name=None, color=None):
    """
    Gibt einen gefaerbten Allianzlink zurueck.

    Name und Farbe werden bei Bedarf aus der Datenbank gefischt.

    @param a_id: Allianz ID
    @param name: Name der Allianz
    @param color: Farbe der Allianz
    @return: gefaerbter HTML-link
    @rtype: C{StringType}
    @raise KeyError: Wenn keine Allianz mit der C{a_id} gefunden wird
    """

    if name is None or color is None:
        sql = "SELECT alliname, color FROM allis WHERE allinr = %s"
        row = util.get_sql_row(sql, a_id)
        if row is None:
            raise KeyError(a_id)
        else:
            name = row[0]
            color = row[1]
    return ausgabe.link("/show/allianz/" + str(a_id), name, color)

def list():
    """Listet alle Allianzen in einer verlinkten Tabelle."""

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
            row = ausgabe.escape_row(row)
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
        cursor.close()
        conn.close()
        print "Es sind", tabelle.length(), "Allianzen in der Datenbank"
        return tabelle.show()
    except rbdb.Error, e:
        util.print_html_error(e)
        return False


class Allianz:
    """Eine Allianz."""

    def __init__(self, a_id):
        """Laed eine Armee

        @param a_id: Allianznummer
        @raise KeyError: Kein Eintrag mit dieser C{a_id} vorhanden.
        """

        self.id = a_id
        """ID der Allianz
        @type: C{IntType}
        """
        sql = "SELECT alliname FROM allis WHERE allinr = %s"
        row = util.get_sql_row(sql, a_id)
        if row is None:
            raise KeyError(a_id)
        else:
            self.name = row[0]
            """Name der Allianz
            @type: C{StringType}
            """


# Aufruf als Skript
if __name__ == '__main__':
    import cgi
    form = cgi.FieldStorage()

    if "list" in form:
        ausgabe.print_header("Allianzliste")
        list()
    elif "id" in form:
        import reich
        from dorf import Dorf
        from armee import Armee

        a_id = form["id"].value
        try:
            allianz = Allianz(a_id)
            allianzname = allianz.name

            ausgabe.print_header("Allianz: " + allianzname)

            print '<table>'
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
        except KeyError, e:
            ausgabe.print_header("Unbekannte Allianz!")


    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
