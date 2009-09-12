"""Einige kleine Hilfsfunktionen"""

import rbdb
from MySQLdb import escape_string

def print_error(e):
    print "Fehler %d: %s" % (e.args[0], e.args[1])

def print_html_error(e):
    print_error(e)
    print "<br />"

def try_execute_safe(cursor, sql, args):
    try:
        cursor.execute(sql, args)
        return cursor.rowcount
    except rbdb.Error, e:
        print_html_error(e)
        return 0

def try_executemany_safe(cursor, sql, arglist):
    try:
        cursor.executemany(sql, arglist[:])
        return cursor.rowcount
    except rbdb.Error, e:
        print_html_error(e)
        return 0

def print_xml(xml_node):
    print xml_node.serialize().replace("<","&lt;").replace(">","&gt;"), "<br />"



def update_usage(r_id, version):
        conn = rbdb.connect()
        cursor = conn.cursor()
        sel_sql = "SELECT r_id FROM versionen WHERE r_id=%s"
        ins_sql = "INSERT INTO versionen (r_id, version) VALUES (%s, %s)"
        # last_seen=now() forces the update even if nothing changed
        upd_sql = "UPDATE versionen SET version=%s,"
        upd_sql += " last_seen=NOW() WHERE r_id=%s"
        try:
            if try_execute_safe(cursor, sel_sql, (r_id,))  == 0:
                try_execute_safe(cursor, ins_sql, (r_id, version))
            else:
                try_execute_safe(cursor, upd_sql, (version, r_id))
        except rbdb.Error, e:
            print_html_error(e)
        conn.close()

def track_client_version(form):
    """Aktualisiert welches Reich mit welcher Kraehenaugenversion
    zum letzten Mal gesendet hat.
    """

    if "agent" in form and "pid" in form:
        r_id = str(int(form["pid"].value.replace("rbspiel","")))
        version = form["agent"].value
        update_usage(r_id, version)

def track_client(node):
    sender_elems = node.xpathEval('sender')
    if len(sender_elems) > 0:
        r_id = sender_elems[0].prop('r_id')
        client_elems = node.xpathEval('client')
        if len(client_elems) > 0:
            name = client_elems[0].prop("name")
            version = client_elems[0].prop("version")
            update_usage(r_id, name + " " + version)


# vim:set shiftwidth=4 expandtab smarttab:
