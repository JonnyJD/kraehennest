#!/usr/bin/env python
"""Eine Modul und Skript um Reichsdaten ein- und auszulesen.

Aufgerufen als Skript kann es als Query-String ein XML-Dokument bekommen
und liest dann die Ritternummern in die Datenbank ein.

Bekommt es ein Feld C{list}, dann werden alle Reiche aufgelistet.

Bekommt es ein Feld C{id}, dann zeigt es die Details eines bestimmten Reiches.
"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import libxml2
from types import StringType
from datetime import timedelta

import rbdb
import util
import ausgabe
from view import allianz


# Reichsstati
S_INAKTIV = 'I' #: Inaktivitaetsliste
S_SCHUTZ = 'S'  #: Schutzliste

def status_string(status):
    """Gibt einen String fuer einen Reichsstatus zurueck
    
    @param status: Status Character aus der Datenbank
    @type status: C{StringType}
    @rtype: C{StringType}
    """
    return {S_INAKTIV: "Inaktiv", S_SCHUTZ: "Schutzliste"
            ,'': None, None: None}[status]

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

def last_turn_color(last_turn):
    """Faerbt den Zeitpunkt des letzten Zuges passend ein
    """
    return ausgabe.date_delta_color_string(last_turn,
            timedelta(days=6), timedelta(days=10))


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

    tabelle = ausgabe.Tabelle()
    tabelle.addColumn(translate("r_id"))
    tabelle.addColumn("Top10")
    tabelle.addColumn("Name")
    if a_id == -1:
        tabelle.addColumn("Allianz")
    tabelle.addColumn("D&ouml;rfer")
    tabelle.addColumn("Armeen")
    tabelle.addColumn("Letzter Zug")
    tabelle.addColumn("Status")
    sql = "SELECT ritter.ritternr, top10, rittername"
    sql += ", allinr, allicolor, alliname"
    sql += ", count(distinct dorf.koords)"
    sql += ", count(distinct h_id)"
    sql += ", letzterzug, inaktiv"
    sql += " FROM ritter"
    sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
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
            row = ausgabe.escape_row(row)
            line = [row[0]]
            line.append(row[1])
            line.append(ausgabe.link("/show/reich/" + str(row[0]), row[2]))
            if a_id == -1:
                line.append(allianz.link(row[3], row[5], row[4]))
            line.append(row[6])
            line.append(row[7])
            line.append(last_turn_color(row[8]))
            line.append(status_string(row[9]))
            tabelle.addLine(line)
            row = cursor.fetchone()
        return tabelle
    except rbdb.Error, e:
        util.print_html_error(e)
        return False


def process_response_xml(node):
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

def process_xml(node):
    """Liest die vom Auge gelieferten Reichsdaten ein.

    @param node: Der Wurzelknoten des zu lesenden Dokuments.
    """

    reiche = node.xpathEval('reich')
    if len(reiche) > 0:
        conn = rbdb.connect()
        cursor = conn.cursor()
        updated = 0
        log = ""
        if util.get_view_type(node) == "top10":
            # resette top10
            # wer nach der Aktualisierung noch den Wert 0 hat
            # ist nicht in den Top10
            sql = "UPDATE ritter SET top10=0"
            util.try_execute_safe(cursor, sql);

    for reich in reiche:
        sqllist = []
        args = ()
        ritter = reich.xpathEval('ritter')[0]
        rittername = ritter.getContent()

        # Ritter
        if not ritter.hasProp("r_id"):
            sql = "SELECT ritternr FROM ritter WHERE rittername = %s"
            if util.try_execute_safe(cursor, sql, (rittername)) == 1:
                r_id = cursor.fetchone()[0]
            else:
                log += "Kann Ritter '" + rittername + "' nicht zuordnen!<br/>\n"
                r_id = None
        else:
            r_id = ritter.prop("r_id")

        if r_id is not None:
            # HACK fuer Koenig, Keiner und Niemand
            # alle Nachrichten der oben genannten gehen an r_id 1 (koenig)!
            if r_id == "1":
                if rittername == "Keiner" and reich.hasProp("name"):
                    if reich.prop("name") == "Keiner":
                        r_id = 2
                        rittername = "Keiner (alt)"
                    else:
                        r_id = 174
                elif rittername == "Niemand":
                    r_id = 172

            # stelle Sicher, dass der Ritter in der DB ist
            sql = "SELECT ritternr FROM ritter WHERE ritternr = %s"
            if util.get_sql_row(sql, (r_id)) is None:
                log += "Ritter '" + rittername + "' wurde eingefuegt!<br />\n"
                sql = "INSERT INTO ritter (ritternr,rittername) VALUES (%s,%s)"
                util.try_execute_safe(cursor, sql, (r_id,rittername))

            sql = "UPDATE ritter SET "

            # Allianz
            allianzen = reich.xpathEval('allianz')
            if len(allianzen) > 0:
                if allianzen[0].hasProp("a_id"):
                    a_id = allianzen[0].prop("a_id")
                else:
                    a_tag = allianzen[0].prop("tag")
                    sql2 = "SELECT allinr FROM allis WHERE alli = %s"
                    if util.try_execute_safe(cursor, sql2, (a_tag)) == 1:
                        a_id = cursor.fetchone()[0]
                    else:
                        log += "Kann Allianz '" + a_tag + "' nicht zuordnen!"
                        log += "<br />\n"
                        a_id = None
                if a_id is not None:
                    sqllist.append("alli=%s")
                    args += a_id,
            # Attribute
            sqllist.append("rittername=%s")
            args += rittername,
            if reich.hasProp("name"):
                sqllist.append("reichsname=%s")
                args += reich.prop("name"),
            if reich.hasProp("level"):
                sqllist.append("reichslevel=%s")
                args += reich.prop("level"),
            if reich.hasProp("top10"):
                sqllist.append("top10=%s")
                args += reich.prop("top10"),
            if reich.hasProp("status"):
                status = reich.prop("status")
                if status == "Inaktiv":
                    sqllist.append("inaktiv='" + S_INAKTIV + "'")
                elif status == "Schutzliste":
                    sqllist.append("inaktiv='" + S_SCHUTZ + "'")
                elif status == "":
                    sqllist.append("inaktiv=NULL")
            if reich.hasProp("last_turn"):
                sqllist.append("letzterzug=%s")
                args += util.parse_date(reich.prop("last_turn")),

            sql += ", ".join(sqllist)
            sql += " WHERE ritternr = %s"
            args += r_id,
            updated += util.try_execute_safe(cursor, sql, args)

    if len(reiche) > 0:
        conn.close()
        log += "Es wurden " + str(updated) + " Reiche aktualisiert."
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
            sql = "SELECT rittername, ritter.alli, alliname, allicolor"
            sql += ", reichsname, reichslevel, top10, letzterzug, inaktiv"
            sql += " FROM ritter LEFT JOIN allis ON ritter.alli = allinr"
            sql += " WHERE ritternr = %s"
            row = util.get_sql_row(sql, r_id)
            if row is None:
                raise KeyError(r_id)
            else:
                self.rittername = row[0]
                """Rittername des Reiches
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
                self.name = row[4]
                """Name des Reiches
                @type: C{StringType}
                """
                self.level = row[5]
                """Level des Reiches
                @type: C{StringType}
                """
                self.top10 = row[6]
                """Platzierung des Reiches
                @type: C{StringType}
                """

                self.last_turn = ausgabe.date_delta_color_string(row[7],
                        timedelta(days=6), timedelta(days=10))
                """Letzter Zug des Reiches
                @type: C{StringType}
                """
                self.status = status_string(row[8])
                """Status des Reiches
                @type: C{StringType}
                """



# Aufruf als Skript: Reich eintragen
if __name__ == '__main__':
    form = cgi.FieldStorage()

    if type(form.value) == StringType:
        # Reichsdaten vom RB Server einlesen
        try:
            root = libxml2.parseDoc(form.value)
            process_response_xml(root)
        except libxml2.parserError:
            print "Es wurden keine gueltigen Daten gesendet. <br />"
    elif "list" in form:
        ausgabe.print_header("Reichsliste")

        reichtabelle = list()
        print "Es sind", reichtabelle.length(), "Reiche in der Datenbank"
        reichtabelle.show()

        ausgabe.print_footer()
    elif "id" in form:
        from model import Armee, Dorf

        r_id = form["id"].value
        try:
            reich = Reich(r_id)
            rittername = cgi.escape(reich.rittername)
            ausgabe.print_header("Reich von: " + rittername)

            print '<table>'
            print '<tr><td>Name: </td>'
            print '<td colspan="4" style="font-weight:bold;">&nbsp;',
            print ausgabe.escape(reich.name) + '</td></tr>'
            print '<tr><td>Allianz: </td><td colspan="4">&nbsp;',
            allianzname = ausgabe.escape(reich.ally_name)
            print allianz.link(reich.ally, allianzname, reich.ally_color),
            print '</td></tr>'
            dorf = Dorf()
            dorftabelle = dorf.list_by_reich(r_id)
            print '<tr><td><a href="#doerfer">D&ouml;rfer:</a> </td>'
            print '<td>&nbsp;&nbsp;' + str(dorftabelle.length()) + '</td>'
            armee = Armee()
            armeetabelle = armee.list_by_reich(r_id)
            print '<td>&nbsp;&nbsp;</td>'
            print '<td><a href="#armeen">Armeen:</a> </td>'
            print '<td>&nbsp;&nbsp;' + str(armeetabelle.length()) + '</td>'
            print '</tr><tr>'
            print '<td>Reichslevel: </td>'
            print '<td>&nbsp;&nbsp;' + str(reich.level) + '</td>'
            print '<td>&nbsp;&nbsp;</td>'
            print '<td>Platzierung: </td>'
            print '<td>&nbsp;&nbsp;' + str(reich.top10) + '</td>'
            print '</tr><tr>'
            print '<td>Letzter Zug: </td>'
            print '<td colspan="3">&nbsp;&nbsp;'+ reich.last_turn + '</td>'
            if reich.status is not None:
                print '</tr><tr>'
                print '<td>Status: </td>'
                print '<td colspan="3">&nbsp;&nbsp;' + reich.status + '</td>'
            print '</tr>'
            print '</table>'

            print '<h2 id="doerfer">D&ouml;rfer</h2>'
            dorftabelle.show()
            print '<h2 id="armeen">Armeen</h2>'
            armeetabelle.show()
        except KeyError, e:
            ausgabe.print_header("Unbekanntes Reich: " + e.args[0])

        ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
