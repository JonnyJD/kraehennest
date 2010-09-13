#!/usr/bin/env python
"""Modul zur Verarbeitung von Benutzerdaten"""

import util
import config


class User:
    """Ein eingeloggter Benutzer des Nestes"""

    def __init__(self, name=None):
        """erstellt eine Instanz fuer den aktuell eingeloggten Benutzer
        """

        if name == None:
            self.name = config.get_username()
            """Benutzername/Login
            @type: C{StringType}
            """
        else:
            self.name = name

        sql = "SELECT r_id, rittername, last_seen"
        sql += " FROM versionen"
        sql += " LEFT JOIN ritter ON r_id = ritternr"
        sql += " WHERE username = %s"
        row = util.get_sql_row(sql, self.name)
        if row is None:
            raise KeyError(self.name)
        else:
            self.r_id = row[0]
            """ID des zugehoerigen Reiches
            @type: C{IntType}
            """
            self.rittername = row[1]
            """Name des zugehoerigen Reiches
            @type: C{StringType}
            """
            self.last_seen_auge = row[2]
            """Wann der Benutzer zum letzten Mal das Auge benutzt hat
            @type: C{DateTime}"""


# vim:set shiftwidth=4 expandtab smarttab:
