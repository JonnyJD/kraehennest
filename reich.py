#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import libxml2
import rbdb
import util

class Reich:
    """Eine Klasse um Reichsdaten ein- und auszulesen.
    """

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
                message =  r_id + ": " + name
                sel_sql = "SELECT rittername FROM ritter WHERE ritternr=%s"
                ins_sql = "INSERT INTO ritter (ritternr, rittername)"
                ins_sql += " VALUES (%s, %s)"
                log_sql = "INSERT INTO logdat (aktion, daten)"
                log_sql += " VALUES ('Ritter eingetragen', %s)"
                upd_sql = "UPDATE ritter SET rittername=%s WHERE ritternr=%s"
                if util.try_execute_safe(cursor, sel_sql, (r_id,)) == 0:
                    # noch nicht in der DB
                    util.try_execute_safe(cursor, ins_sql, (r_id, name)) == 1
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
    print "Content-type: text/plain\n"
    form = cgi.FieldStorage()
    root = None

    try:
        root = libxml2.parseDoc(form.value)
    except libxml2.parserError:
        print "Es wurden keine gueltigen Daten gesendet. <br />"

    if root != None:
        reich = Reich()
        reich.process_xml(root)


# vim:set shiftwidth=4 expandtab smarttab:
