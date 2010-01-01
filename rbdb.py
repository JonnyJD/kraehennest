"""Wrapper fuer eine RB Datenbankverbindung zu MySQL"""

import config
import sys
import MySQLdb
import MySQLdb.cursors

Error = MySQLdb.Error
DictCursor = MySQLdb.cursors.DictCursor

def connect():
    """Stellt eine Verbindung her zur RB Datenbank.

    """
    try:
        conn = MySQLdb.connect (host   = config.db_host,
                                user   = config.db_user,
                                passwd = config.db_passwd,
                                db     = config.db)
        conn.set_character_set("utf8")
    except MySQLdb.Error, e:
        print "Fehler %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    return conn

# vim:set shiftwidth=4 expandtab smarttab: