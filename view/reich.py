#!/usr/bin/env python
"""Eine Modul um Reichsdaten auszugeben.
"""

from datetime import timedelta

import rbdb
import util
import ausgabe

import allianz
from model.reich import S_INAKTIV, S_SCHUTZ, S_NPC


def status_string(status):
    """Gibt einen String fuer einen Reichsstatus zurueck
    
    @param status: Status Character aus der Datenbank
    @type status: C{StringType}
    @rtype: C{StringType}
    """
    return {S_INAKTIV: "Inaktiv", S_SCHUTZ: "Schutzliste",
            S_NPC: "NPC", '': None, None: None}[status]

def get_ritter_id_form(rittername):
    """
    Gibt das HTML-Formular mit dem Ritternamen nachgeschlagen werden

    @param rittername: Der Name eines Ritters
    @return: Das HTML-Formular um nach dem C{ritternamen} zu suchen.
    @rtype: C{StringType}
    """

    form ='''<form method="post"
        action ="http://www.ritterburgwelt.de/rb/ajax_backend.php"
        target="_blank">
        <input type="hidden" name="_func" value="vorschlagSuche">
        <input type="hidden" name="_args[0]" value="sucheBenutzerName">
        <input type="hidden" name="_args[1]"'''
    form += ' value="' + rittername + '">'
    form += '<input type="submit" value="hole ID"></form>'
    return form

def translate(column):
    """Uebersetzt den Datenbanknamen fuer die Anzeige
    
    @param column: Name in der Datenbank (oder Variable)
    @return: Anzeigename (mit HTML entities)
    @rtype: C{StringType}
    """
    dictionary = {'r_id': "ID"}
    if column in dictionary:
        return dictionary[column]
    else:
        return column.capitalize()

def last_turn_color(last_turn):
    """Faerbt den Zeitpunkt des letzten Zuges passend ein
    """
    return ausgabe.date_delta_color_string(last_turn,
            timedelta(days=6), timedelta(days=10))


def list():
    """Gibt eine Tabelle aller Reiche und ihrer Herrscher.
    
    @rtype: L{Tabelle<ausgabe.Tabelle>}
    """
    return list_by_allianz(-1)

def list_by_allianz(a_id):
    """Liste alle Reiche die Mitglied einer bestimmten Allianz sind.
    
    @param a_id: Allianznummer
    @rtype: L{Tabelle<ausgabe.Tabelle>}
    """

    tabelle = ausgabe.Tabelle()
    tabelle.addColumn(translate("r_id"))
    tabelle.addColumn("Top10")
    tabelle.addColumn("Name")
    if a_id == -1:
        tabelle.addColumn("Allianz")
    tabelle.addColumn("D&ouml;rfer")
    tabelle.addColumn("Armeen")
    tabelle.addColumn("Letzter Zug")
    tabelle.addColumn("Status")
    sql = "SELECT ritter.ritternr, top10, rittername"
    sql += ", allinr, allicolor, alliname"
    sql += ", count(distinct dorf.koords)"
    sql += ", count(distinct h_id)"
    sql += ", letzterzug, inaktiv"
    sql += " FROM ritter"
    sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
    sql += " LEFT JOIN dorf ON ritter.ritternr = dorf.ritternr"
    sql += " LEFT JOIN armeen ON ritter.ritternr = r_id"
    sql += " WHERE (top10 > 0"
    sql += " OR ritter.alli <> 0" # noetig fuer gesamtliste (-1)
    sql += " OR inaktiv = 'P'" # SL/NPC Reiche? (alte DB)
    sql += " OR ritter.ritternr IN (2,7,172,174,175))"
    if a_id != -1:
        sql += " AND allinr =%s "
    sql += " GROUP BY ritter.ritternr, top10, rittername"
    sql += ", allinr, allicolor, alliname"
    sql += " ORDER BY rittername"
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        if a_id != -1:
            cursor.execute(sql, a_id)
        else:
            cursor.execute(sql)
        row = cursor.fetchone()
        while row != None:
            row = ausgabe.escape_row(row)
            line = [row[0]]
            line.append(row[1])
            line.append(ausgabe.link("/show/reich/%d" % row[0], row[2]))
            if a_id == -1:
                line.append(allianz.link(row[3], row[5], row[4]))
            line.append(row[6])
            line.append(row[7])
            line.append(last_turn_color(row[8]))
            line.append(status_string(row[9]))
            tabelle.addLine(line)
            row = cursor.fetchone()
        return tabelle
    except rbdb.Error, e:
        util.print_html_error(e)
        return False


# vim:set shiftwidth=4 expandtab smarttab:
