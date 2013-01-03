#!/usr/bin/env python
"""Eine Modul um Reichsdaten einzulesen.
"""

import rbdb
import util
from model.reich import S_INAKTIV, S_SCHUTZ


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


# vim:set shiftwidth=4 expandtab smarttab:
