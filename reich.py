#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import libxml2
import rbdb
import util
import ausgabe

def get_ritter_id_form(rittername):
    form ='''<form method="post"
        action ="http://www.ritterburgwelt.de/rb/ajax_backend.php"
        target="_blank">
        <input type="hidden" name="_func" value="vorschlagSuche">
        <input type="hidden" name="_args[0]" value="sucheBenutzerName">
        <input type="hidden" name="_args[1]"'''
    form += ' value="' + rittername + '">'
    form += '<input type="submit" value="hole ID"></form>'
    return form

class Reich:
    """Eine Klasse um Reichsdaten ein- und auszulesen.
    """

    def get_name(self, r_id):
        sql = "SELECT rittername FROM ritter WHERE ritternr = %s"
        row = util.get_sql_row(sql, r_id)
        if row:
            return row[0]
        else:
            return "[unbekannter Ritter]"

    def list(self):
        return self.list_by_allianz(-1)

    def list_by_allianz(self, a_id):
        tabelle = ausgabe.Tabelle()
        tabelle.addColumn("r_id")
        tabelle.addColumn("Top10")
        tabelle.addColumn("Name")
        tabelle.addColumn("D&ouml;rfer")
        tabelle.addColumn("Armeen")
        if a_id == -1:
            tabelle.addColumn("Allianz")
        sql = "SELECT ritter.ritternr, top10, rittername"
        sql += ", allinr, allicolor, alliname"
        sql += ", count(distinct dorf.koords)"
        sql += ", count(distinct h_id)"
        sql += " FROM ritter"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        sql += " LEFT JOIN dorf ON ritter.ritternr = dorf.ritternr"
        sql += " LEFT JOIN armeen ON ritter.ritternr = r_id"
        sql += " WHERE (top10 > 0"
        sql += " OR ritter.ritternr"
        sql += " IN (0,1,2,113,143,160,172,174,88,159,174,1152))"
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
                zelle = '<a href="' + ausgabe.prefix + '/show/reich/'
                zelle += str(row[0]) + '">'
                zelle += str(row[2]) + '</a>'
                line.append(zelle)
                if a_id == -1:
                    zelle = '<a href="' + ausgabe.prefix + '/show/allianz/'
                    zelle += str(row[3]) + '">'
                    zelle += '<div style="color:' + row[4] + ';">'
                    zelle += row[5] + '</div></a>'
                    line.append(zelle)
                line.append(row[6])
                line.append(row[7])
                tabelle.addLine(line)
                row = cursor.fetchone()
            return tabelle
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def process_xml(self, node):
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



# Aufruf als Skript: Reich eintragen
if __name__ == '__main__':
    form = cgi.FieldStorage()
    root = None

    if "list" in form:
        ausgabe.print_header("Reichsliste")

        reich = Reich()
        reichtabelle = reich.list()
        print "Es sind", reichtabelle.length(), "Reiche in der Datenbank"
        reichtabelle.show()

    elif "id" in form:
        from armee import Armee
        from dorf import Dorf

        r_id = form["id"].value
        reich = Reich()
        name = reich.get_name(r_id)
        ausgabe.print_header('Reich: ' + name)

        print '<table>'
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
    else:
        # Reichsdaten vom RB Server einlesen
        try:
            root = libxml2.parseDoc(form.value)
        except libxml2.parserError:
            print "Es wurden keine gueltigen Daten gesendet. <br />"

        if root != None:
            reich = Reich()
            reich.process_xml(root)

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
