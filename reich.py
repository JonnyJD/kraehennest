#!/usr/bin/python
"""Eine Modul und Skript um Reichsdaten ein- und auszulesen.

Aufgerufen als Skript kann es als Query-String ein XML-Dokument bekommen
und liest dann die Ritternummern in die Datenbank ein.

Bekommt es ein Feld C{list}, dann werden alle Reiche aufgelistet.

Bekommt es ein Feld C{id}, dann zeigt es die Details eines bestimmten Reiches.
"""

#import cgitb
#cgitb.enable()

import cgi
import libxml2
import rbdb
import util
import ausgabe
from types import StringType

def get_ritter_id_form(rittername):
    """
    Gibt das HTML-Formular mit dem Ritternamen nachgeschlagen werden

    @param rittername: Der Name eines Ritters
    @return: Das HTML-Formular um nach dem C{ritternamen} zu suchen.
    @rtype: C{StringType}
    """

    form ='''<form method="post"
        action ="http://www.ritterburgwelt.de/rb/ajax_backend.php"
        target="_blank">
        <input type="hidden" name="_func" value="vorschlagSuche">
        <input type="hidden" name="_args[0]" value="sucheBenutzerName">
        <input type="hidden" name="_args[1]"'''
    form += ' value="' + rittername + '">'
    form += '<input type="submit" value="hole ID"></form>'
    return form

def translate(column):
    """Uebersetzt den Datenbanknamen fuer die Anzeige
    
    @param column: Name in der Datenbank (oder Variable)
    @return: Anzeigename (mit HTML entities)
    @rtype: C{StringType}
    """
    dictionary = {'r_id': "ID"}
    if column in dictionary:
        return dictionary[column]
    else:
        return column.capitalize()


def list():
    """Gibt eine Tabelle aller Reiche und ihrer Herrscher.
    
    @rtype: L{Tabelle<ausgabe.Tabelle>}
    """
    return list_by_allianz(-1)

def list_by_allianz(a_id):
    """Liste alle Reiche die Mitglied einer bestimmten Allianz sind.
    
    @param a_id: Allianznummer
    @rtype: L{Tabelle<ausgabe.Tabelle>}
    """

    import allianz

    tabelle = ausgabe.Tabelle()
    tabelle.addColumn(translate("r_id"))
    tabelle.addColumn("Top10")
    tabelle.addColumn("Name")
    if a_id == -1:
        tabelle.addColumn("Allianz")
    tabelle.addColumn("D&ouml;rfer")
    tabelle.addColumn("Armeen")
    sql = "SELECT ritter.ritternr, top10, rittername"
    sql += ", allinr, allicolor, alliname"
    sql += ", count(distinct dorf.koords)"
    sql += ", count(distinct h_id)"
    sql += " FROM ritter"
    sql += " JOIN allis ON ritter.alli = allis.allinr"
    sql += " LEFT JOIN dorf ON ritter.ritternr = dorf.ritternr"
    sql += " LEFT JOIN armeen ON ritter.ritternr = r_id"
    sql += " WHERE (top10 > 0"
    sql += " OR ritter.alli <> 0" # noetig fuer gesamtliste (-1)
    sql += " OR inaktiv = 'P'" # SL/NPC Reiche? (alte DB)
    sql += " OR ritter.ritternr IN (2,172,174,175))"
    if a_id != -1:
        sql += " AND allinr =%s "
    sql += " GROUP BY ritter.ritternr, top10, rittername"
    sql += ", allinr, allicolor, alliname"
    sql += " ORDER BY rittername"
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        if a_id != -1:
            cursor.execute(sql, a_id)
        else:
            cursor.execute(sql)
        row = cursor.fetchone()
        while row != None:
            line = [row[0]]
            line.append(row[1])
            line.append(ausgabe.link("/show/reich/" + str(row[0]), row[2]))
            if a_id == -1:
                line.append(allianz.link(row[3], row[5], row[4]))
            line.append(row[6])
            line.append(row[7])
            tabelle.addLine(line)
            row = cursor.fetchone()
        return tabelle
    except rbdb.Error, e:
        util.print_html_error(e)
        return False


def process_xml(node):
    """Liest die Reichsnummern aus einem XML Dokument in die Datenbank ein.

    @param node: Der Wurzelknoten des zu lesenden Dokuments.
    """

    items = node.xpathEval('/response/content/item')
    if len(items) > 0:
        conn = rbdb.connect()
        cursor = conn.cursor()
        log = ""

        for item in items:
            subitems = item.xpathEval('item')
            name = subitems[0].getContent()
            r_id = subitems[1].getContent()
            if len(r_id) > 0:
                message =  r_id + ": " + name
                r_id = int(r_id)
                sel_sql = "SELECT rittername FROM ritter WHERE ritternr=%s"
                ins_sql = "INSERT INTO ritter (ritternr, rittername)"
                ins_sql += " VALUES (%s, %s)"
                log_sql = "INSERT INTO logdat (aktion, daten)"
                log_sql += " VALUES ('Ritter eingetragen', %s)"
                upd_sql = "UPDATE ritter SET rittername=%s"
                upd_sql += " WHERE ritternr=%s"
                if util.try_execute_safe(cursor, sel_sql, (r_id,)) == 0:
                    # noch nicht in der DB
                    util.try_execute_safe(cursor, ins_sql, (r_id, name))
                    if cursor.rowcount == 1:
                        log += message + " eingetragen\n"
                        util.try_execute_safe(cursor, log_sql, (message,))
                    else:
                        log += message + " NICHT eingetragen!\n"
                else:
                    # schon in der DB
                    row = cursor.fetchone()
                    if row[0] != name:
                        util.try_execute_safe(cursor, upd_sql, (name, r_id))
                        if cursor.rowcount == 1:
                            log += message + " aktualisiert\n"
                            log += "\t alter Name war: " + row[0] + "\n"
                        else:
                            log += message + " NICHT aktualisiert!\n"
        conn.close()
        print log


class Reich:
    """Eine Klasse fuer Daten rund um ein Reich, inklusive Ritter."""

    def __init__(self, r_id=None):
        """Holt die Daten eines Reiches

        @param r_id: Ritternummer
        @raise KeyError: Kein Eintrag mit dieser C{r_id} vorhanden.
        """

        if r_id is not None:
            self.id = r_id
            """ID des Reiches
            @type: C{IntType}
            """
            sql = "SELECT rittername, allinr, alliname, allicolor"
            sql += " FROM ritter JOIN allis ON ritter.alli = allinr"
            sql += " WHERE ritternr = %s"
            row = util.get_sql_row(sql, r_id)
            if row is None:
                raise KeyError(r_id)
            else:
                self.name = row[0]
                """Name des Reiches
                @type: C{StringType}
                """
                self.ally = row[1]
                """ID der Allianz in der das Reich ist
                @type: C{IntType}
                """
                self.ally_name = row[2]
                """Name der Allianz in der das Reich ist
                @type: C{StringType}
                """
                self.ally_color = row[3]
                """Farbe der Allianz in der das Reich ist
                @type: C{StringType}
                """



# Aufruf als Skript: Reich eintragen
if __name__ == '__main__':
    form = cgi.FieldStorage()

    if type(form.value) == StringType:
        # Reichsdaten vom RB Server einlesen
        try:
            root = libxml2.parseDoc(form.value)
            process_xml(root)
        except libxml2.parserError:
            print "Es wurden keine gueltigen Daten gesendet. <br />"
    elif "list" in form:
        ausgabe.print_header("Reichsliste")

        reichtabelle = list()
        print "Es sind", reichtabelle.length(), "Reiche in der Datenbank"
        reichtabelle.show()

        ausgabe.print_footer()
    elif "id" in form:
        from armee import Armee
        from dorf import Dorf
        import allianz

        r_id = form["id"].value
        try:
            reich = Reich(r_id)
            ausgabe.print_header('Reich: ' + reich.name)

            print '<table>'
            print '<tr><td>Allianz</td><td>',
            print allianz.link(reich.ally, reich.ally_name, reich.ally_color),
            print '</td></tr>'
            dorf = Dorf()
            dorftabelle = dorf.list_by_reich(r_id)
            print '<tr><td><a href="#doerfer">D&ouml;rfer</a></td>'
            print '<td>' + str(dorftabelle.length()) + '</td></tr>'
            armee = Armee()
            armeetabelle = armee.list_by_reich(r_id)
            print '<tr><td><a href="#armeen">Armeen</a></td>'
            print '<td>' + str(armeetabelle.length()) + '</td></tr>'
            print '</table>'

            print '<h2 id="doerfer">D&ouml;rfer</h2>'
            dorftabelle.show()
            print '<h2 id="armeen">Armeen</h2>'
            armeetabelle.show()
        except KeyError, e:
            ausgabe.print_header("Unbekanntes Reich: " + e.args[0])

        ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
