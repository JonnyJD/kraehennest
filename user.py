#!/usr/bin/python
"""Modul zur Verarbeitung von Benutzerdaten"""

import util
import config


def last_seen_auge(username=None):
    """Gibt zurueck wann der Benutzer zum letzten Mal das Auge benutzt hat

    @rtype: C{DateTime}
    """

    if username is None:
        username = config.get_username()
    sql = "SELECT last_seen FROM versionen WHERE username = %s"
    row = util.get_sql_row(sql, username)
    if row is None:
        return None
    else:
        return row[0]


# vim:set shiftwidth=4 expandtab smarttab:
