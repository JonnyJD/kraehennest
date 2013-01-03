#!/usr/bin/env python
"""Ein Modul um Allianzdaten auszugeben und zu listen."""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import util
import ausgabe


def link(a_id, name=None, color=None):
    """
    Gibt einen gefaerbten Allianzlink zurueck.

    Name und Farbe werden bei Bedarf aus der Datenbank gefischt.

    @param a_id: Allianz ID
    @param name: Name der Allianz
    @param color: Farbe der Allianz
    @return: gefaerbter HTML-link
    @rtype: C{StringType}
    @raise KeyError: Wenn keine Allianz mit der C{a_id} gefunden wird
    """

    if a_id is None:
        return "?"
    elif name is None or color is None:
        sql = "SELECT alliname, allicolor FROM allis WHERE allinr = %s"
        row = util.get_sql_row(sql, a_id)
        if row is None:
            name = str(a_id)
	    color = None
        else:
            name = row[0]
            color = row[1]
    return ausgabe.link("/show/allianz/" + str(a_id), name, color)


# vim:set shiftwidth=4 expandtab smarttab:
