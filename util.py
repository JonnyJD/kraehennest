"""Einige kleine Hilfsfunktionen"""

import rbdb
from MySQLdb import escape_string

def print_error(e):
    print "Fehler %d: %s" % (e.args[0], e.args[1])

def print_html_error(e):
    print_error(e)
    print "<br />"

def addslashes(text):
    """Funktion um fuer MySQL gefaehrliche Zeichen zu maskieren"""
    return escape_string(text)



def update_usage(r_id, version):
        conn = rbdb.connect()
        cursor = conn.cursor()
        sel_sql = "SELECT r_id FROM versionen WHERE r_id=" + r_id
        ins_sql = "INSERT INTO versionen (r_id, version)"
        ins_sql += " VALUES (" + r_id + ", '" + version + "')"
        # last_seen=now() forces the update even if nothing changed
        upd_sql = "UPDATE versionen SET version='" + version + "',"
        upd_sql += " last_seen=NOW() WHERE r_id=" + r_id
        try:
            cursor.execute(sel_sql)
            if cursor.rowcount == 0:
                cursor.execute(ins_sql)
            else:
                cursor.execute(upd_sql)
        except rbdb.Error, e:
            print_html_error(e)
        conn.close()

def track_client_version(form):
    """Aktualisiert welches Reich mit welcher Kraehenaugenversion
    zum letzten Mal gesendet hat.
    """

    if "agent" in form and "pid" in form:
        r_id = str(int(form["pid"].value.replace("rbspiel","")))
        version = addslashes(form["agent"].value)
        update_usage(r_id, version)

def track_client(node):
    sender_elems = node.getElementsByTagName("sender")
    if sender_elems.length > 0:
        r_id = sender_elems[0].getAttribute("r_id")
        client_elems = node.getElementsByTagName("client")
        if client_elems.length > 0:
            name = client_elems[0].getAttribute("name")
            version = client_elems[0].getAttribute("version")
            update_usage(r_id, name + " " + version)


# vim:set shiftwidth=4 expandtab smarttab:
