#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import libxml2
import rbdb
import util

class Reich:
    """Eine Klasse um Reichsdaten ein- und auszulesen.
    
    Einlesen:

    Auslesen:
    
    Beenden:
    """
    def __try_execute(self, cursor, sql):
        try:
            cursor.execute(sql)
            return cursor.rowcount
        except rbdb.Error, e:
            util.print_html_error(e)
            return 0


    def process_xml(self, node):
        items = node.xpathEval('/response/content/item')
        if len(items) > 0:
            conn = rbdb.connect()
            cursor = conn.cursor()
            log = ""

            for item in items:
                subitems = item.xpathEval('item')
                name = subitems[0].getContent()
                safe_name = util.addslashes(name)
                r_id = util.addslashes(subitems[1].getContent())
                message =  r_id + ": " + name
                sel_sql = "SELECT rittername FROM ritter"
                sel_sql += " WHERE ritternr=" + r_id
                ins_sql = "INSERT INTO ritter (ritternr, rittername)"
                ins_sql += " VALUES (" + r_id + ", '" + s_name + "')"
                log_sql = "INSERT INTO logdat (aktion, daten)"
                log_sql += " VALUES ('Ritter eingetragen', '" + message + "')"
                upd_sql = "UPDATE ritter SET rittername='" + s_name + "'" 
                upd_sql += " WHERE ritternr=" + r_id
                self.__try_execute(cursor, sel_sql)
                if cursor.rowcount == 0:
                    # noch nicht in der DB
                    self.__try_execute(cursor, ins_sql)
                    if cursor.rowcount == 1:
                        log += message + " eingetragen\n"
                        self.__try_execute(cursor, log_sql)
                    else:
                        log += message + " NICHT eingetragen!\n"
                else:
                    # schon in der DB
                    row = cursor.fetchone()
                    if row[0] != name:
                        self.__try_execute(cursor, upd_sql)
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
