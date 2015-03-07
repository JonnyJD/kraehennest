#!/usr/bin/env python
"""Reichsdaten
"""

from datetime import timedelta
import util
import ausgabe


# Reichsstati
S_INAKTIV = 'I' #: Inaktivitaetsliste
S_SCHUTZ = 'S'  #: Schutzliste
S_NPC = 'N'     #: NPC

class Reich:
    """Eine Klasse fuer Daten rund um ein Reich, inklusive Ritter."""

    def __init__(self, r_id=None):
        """Holt die Daten eines Reiches

        @param r_id: Ritternummer
        @raise KeyError: Kein Eintrag mit dieser C{r_id} vorhanden.
        """

        if r_id is not None:
            self.id = r_id
            """ID des Reiches
            @type: C{IntType}
            """
            sql = "SELECT rittername, ritter.alli, alliname, allicolor"
            sql += ", reichsname, reichslevel, top10, letzterzug, inaktiv"
            sql += " FROM ritter LEFT JOIN allis ON ritter.alli = allinr"
            sql += " WHERE ritternr = %s"
            row = util.get_sql_row(sql, r_id)
            if row is None:
                raise KeyError(r_id)
            else:
                self.rittername = row[0]
                """Rittername des Reiches
                @type: C{StringType}
                """
                self.ally = row[1]
                """ID der Allianz in der das Reich ist
                @type: C{IntType}
                """
                self.ally_name = row[2]
                """Name der Allianz in der das Reich ist
                @type: C{StringType}
                """
                self.ally_color = row[3]
                """Farbe der Allianz in der das Reich ist
                @type: C{StringType}
                """
                self.name = row[4]
                """Name des Reiches
                @type: C{StringType}
                """
                self.level = row[5]
                """Level des Reiches
                @type: C{StringType}
                """
                self.top10 = row[6]
                """Platzierung des Reiches
                @type: C{StringType}
                """

                self.last_turn = ausgabe.date_delta_color_string(row[7],
                        timedelta(days=6), timedelta(days=10))
                """Letzter Zug des Reiches
                @type: C{StringType}
                """
		#self.status = status_string(row[8])
		self.status = row[8]
                """Status des Reiches
                @type: C{StringType}
                """


# vim:set shiftwidth=4 expandtab smarttab:
