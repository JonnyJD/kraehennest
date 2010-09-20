#!/usr/bin/env python
"""Ein Modul um Rezeptdaten ein- und auszulesen"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import util
#from datetime import date, datetime, timedelta
import ausgabe


def translate(column):
    """Uebersetzt den Datenbanknamen fuer die Anzeige
    
    @param column: Name in der Datenbank (oder Variable)
    @return: Anzeigename (mit HTML entities)
    @rtype: C{StringType}
    """
    dictionary = {'rezept_id': "ID", 'rezept.name': "Rezeptname"}
    if column in dictionary:
        return dictionary[column]
    else:
        return column.capitalize()

def __list(cols, waren):
    """Erstellt eine Tabelle der Rezepte
    
    @rtype: L{Tabelle<ausgabe.Tabelle>}
    """

    tabelle = ausgabe.Tabelle()
    for col in cols:
        tabelle.addColumn(translate(col))
    offset = 0
    if "rezept.name" not in cols:
        offset -= 1 # Rezeptname faellt bei Gegenstaenden weg
    if "zeit" in cols:
        offset += 1 # Rezeptname faellt bei Gegenstaenden weg
    i = 0
    while i < len(waren):
        row = ausgabe.escape_row(waren[i])
        line = [row[0]]
        if "rezept.name" in cols or "zeit" in cols:
            line.append(row[1])
        if "rezept.name" in cols and "zeit" in cols:
            line.append(row[2])
        produkt = ""
        kosten = ""
        current_id = row[0]
        while i < len(waren) and current_id == waren[i][0]:
            row = ausgabe.escape_row(waren[i])
            menge = row[3+offset]
            if menge > 0:
                if len(produkt) > 0: produkt += "<br />"
                produkt += str(menge) + " " + row[2+offset]
            else:
                if len(kosten) > 0: kosten += "<br />"
                kosten += str(menge*-1) + " " + row[2+offset]
            i += 1
        line.append(produkt)
        line.append(kosten)
        tabelle.addLine(line)
    return tabelle

def list_all():
    """Gibt eine Tabelle aller Rezepte aus
    
    @return: L{Tabelle<ausgabe.Tabelle>}
    """

    cols = ["rezept_id", "rezept.name", "zeit"]
    cols += ["ware.name", "produktion.menge"]
    sql = "SELECT " + ", ".join(cols)
    sql += " FROM rezept"
    sql += " JOIN produktion ON rezept.rezept_id = produktion.rezept"
    sql += " JOIN ware ON produktion.ware = ware.ware_id"
    sql += " ORDER BY rezept_id ASC, ware_id ASC"
    waren = util.get_sql_rows(sql)
    cols = ["rezept_id", "rezept.name", "zeit"]
    cols += ["Produkt", "Kosten"]
    return __list(cols, waren)

def list_gueter():
    """Gibt eine Tabelle aller Gueter aus
    
    @return: L{Tabelle<ausgabe.Tabelle>}
    """

    cols = ["rezept_id", "rezept.name"]
    cols += ["ware.name", "produktion.menge"]
    sql = "SELECT " + ", ".join(cols)
    sql += " FROM rezept"
    sql += " JOIN produktion ON rezept.rezept_id = produktion.rezept"
    sql += " JOIN ware ON produktion.ware = ware.ware_id"
    sql += " WHERE rezept_id < 100"
    sql += " ORDER BY rezept_id ASC, ware_id ASC"
    waren = util.get_sql_rows(sql)
    cols = ["rezept_id", "rezept.name"]
    cols += ["Produkt", "Kosten"]
    return __list(cols, waren)

def list_gegenstaende():
    """Gibt eine Tabelle aller Gegenstaende aus
    
    @return: L{Tabelle<ausgabe.Tabelle>}
    """

    cols = ["rezept_id", "zeit", "ware.name", "produktion.menge"]
    sql = "SELECT " + ", ".join(cols)
    sql += " FROM rezept"
    sql += " JOIN produktion ON rezept.rezept_id = produktion.rezept"
    sql += " JOIN ware ON produktion.ware = ware.ware_id"
    sql += " WHERE rezept_id > 100 AND rezept_id < 4000"
    sql += " ORDER BY rezept_id ASC, ware_id ASC"
    waren = util.get_sql_rows(sql)
    cols = ["rezept_id", "zeit"]
    cols += ["Produkt", "Kosten"]
    return __list(cols, waren)

def list_runen():
    """Gibt eine Tabelle aller Runen aus
    
    @return: L{Tabelle<ausgabe.Tabelle>}
    """

    cols = ["rezept_id", "rezept.name", "zeit"]
    cols += ["ware.name", "produktion.menge"]
    sql = "SELECT " + ", ".join(cols)
    sql += " FROM rezept"
    sql += " JOIN produktion ON rezept.rezept_id = produktion.rezept"
    sql += " JOIN ware ON produktion.ware = ware.ware_id"
    # TODO: interessant sind hier wohl nur die veraenderbaren: id < 4000
    sql += " WHERE rezept.name LIKE %s"
    args = ("%RUNE")    # %-Zeichen vertraegt sich nicht mit get_sql_rows sonst
    sql += " ORDER BY rezept_id ASC, ware_id ASC"
    waren = util.get_sql_rows(sql, args)
    cols = ["rezept_id", "rezept.name", "zeit"]
    cols += ["Produkt", "Kosten"]
    return __list(cols, waren)

# vim:set shiftwidth=4 expandtab smarttab:
