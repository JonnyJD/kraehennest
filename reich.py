#!/usr/bin/python

#import cgitb
#cgitb.enable()

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

    def list(self):
        tabelle = ausgabe.Tabelle()
        tabelle.addColumn("r_id")
        tabelle.addColumn("Top10")
        tabelle.addColumn("Name")
        tabelle.addColumn("Allianz")
        sql = "SELECT ritternr, top10, rittername, allinr, allicolor, alliname"
        sql += " FROM ritter"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE top10 > 0"
        sql += " OR ritternr IN (1,2,113,143,160,172,174,88,159,174,1152)"
        sql += " ORDER BY rittername"
        try:
            conn = rbdb.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            while row != None:
                line = [row[0]]
                line.append(row[1])
                zelle = '<a href="reich/' + str(row[0]) + '">'
                zelle += str(row[2]) + '</a>'
                line.append(zelle)
                zelle = '<a href="allianz/' + str(row[3]) + '">'
                zelle += '<div style="color:' + row[4] + ';">'
                zelle += row[5] + '</div></a>'
                line.append(zelle)
                tabelle.addLine(line)
                row = cursor.fetchone()
            print "Es sind", tabelle.length(), "Reiche in der Datenbank"
            return tabelle.show()
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
    print 'Content-type: text/html; charset=utf-8\n'
    print '<html><head>'
    print '<link rel="stylesheet" type="text/css" href="../stylesheet">'

    form = cgi.FieldStorage()
    root = None

    if "list" in form:
        print '<title>Reichsliste</title>'
        print '</head>'
        print '<body>'

        reich = Reich()
        reich.list()
    elif "id" in form:
        from armee import Armee

        r_id = form["id"].value

        print '<title>Reich ' + r_id + '</title>'
        print '</head>'
        print '<body>'

        armee = Armee()
        armeetabelle = armee.list_by_reich(r_id)
        print "Anzahl Armeen:", armeetabelle.length()
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

    print '</body></html>'


# vim:set shiftwidth=4 expandtab smarttab:
