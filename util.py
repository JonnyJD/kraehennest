"""Einige kleine Hilfsfunktionen"""

import datetime
import rbdb
from MySQLdb import escape_string


def print_error(e):
    """Gibt Code und Meldung eines Fehlers aus
    """
    print "Fehler %d: %s" % (e.args[0], e.args[1])

def print_html_error(e):
    """Gibt Code und Meldung eines Fehler in HTML aus
    """
    print_error(e)
    print "<br />"

def print_xml(xml_node):
    """Gibt einen XML-Knoten aus

    @rtype: C{StringType}
    """
    print xml_node.serialize().replace("<","&lt;").replace(">","&gt;"), "<br />"


def get_view_type(node):
    """Gibt die Art der Sichtung aus einem XML-Dokumente aus

    @rtype: C{StringType}
    """
    sicht_elems = node.xpathEval('/data/auge/sicht')
    if len(sicht_elems) > 0:
        return sicht_elems[0].prop("typ")
    else:
        return "keine"


def parse_date(rb_date):
    """Parst das "Realdatum" aus einem RB-Datumsstring

    @rtype: C{datetime.date}
    """

    datum = rb_date.split(",")[1].strip().split(".")
    year = int(datum[2]) + 1653
    month = int(datum[1])
    day = int(datum[0])

    return datetime.date(year, month, day)


######################################################################
#{ SQL
######################################################################

def try_execute_safe(cursor, sql, args):
    """Fuehrt eine Datenbankquery aus

    @return: Anzahl der Aenderungen
    @rtype: C{IntType}
    """
    try:
        cursor.execute(sql, args)
        return cursor.rowcount
    except rbdb.Error, e:
        print sql, "<br />", args, "<br />"
        print_html_error(e)
        return 0

def try_executemany_safe(cursor, sql, arglist):
    """Fuehrt eine mehrere Datenbankqueries aus

    @return: Anzahl der Aenderungen
    @rtype: C{IntType}
    """
    try:
        cursor.executemany(sql, arglist[:])
        return cursor.rowcount
    except rbdb.Error, e:
        print_html_error(e)
        return 0

def get_sql_row(sql, args):
    """Fuehrt eine Datenbankabfrage aus

    @return: Gewonnene Werte
    @rtype: C{List}
    """
    conn = rbdb.connect()
    cursor = conn.cursor()
    try_execute_safe(cursor, sql, args)
    row = cursor.fetchone()
    conn.close()
    return row

def sql_execute(sql, args):
    """Fuehrt eine Datenbankaktion aus

    @return: Anzahl der Aenderungen
    @rtype: C{List}
    """
    conn = rbdb.connect()
    cursor = conn.cursor()
    try_execute_safe(cursor, sql, args)
    count = cursor.rowcount
    conn.close()
    return count


######################################################################
#{ Augennutzung
######################################################################

def update_usage(r_id, version):
    """Aktualisiert die Benutzertabelle
    
    @param r_id: ID des Ritters
    @param version: Version des Kraehenauges
    """

    conn = rbdb.connect()
    cursor = conn.cursor()
    sel_sql = "SELECT r_id FROM versionen WHERE r_id=%s"
    ins_sql = "INSERT INTO versionen (r_id, version) VALUES (%s, %s)"
    # last_seen=now() forces the update even if nothing changed
    upd_sql = "UPDATE versionen SET version=%s,"
    upd_sql += " last_seen=NOW() WHERE r_id=%s"
    if try_execute_safe(cursor, sel_sql, (r_id,))  == 0:
        try_execute_safe(cursor, ins_sql, (r_id, version))
    else:
        try_execute_safe(cursor, upd_sql, (version, r_id))
    conn.close()

def track_client_version(form):
    """Aktualisiert welches Reich mit welcher Kraehenaugenversion
    zum letzten Mal gesendet hat.

    @param form: Das gesendete Formular
    """

    if "agent" in form and "pid" in form:
        r_id = str(int(form["pid"].value.replace("rbspiel","")))
        version = form["agent"].value
        update_usage(r_id, version)

def track_client(node):
    """Aktualisiert welches Reich mit welcher Kraehenaugenversion
    zum letzten Mal gesendet hat.

    @param node: der passende Knoten im XML-Dokument
    """

    sender_elems = node.xpathEval('sender')
    if len(sender_elems) > 0:
        r_id = sender_elems[0].prop('r_id')
        client_elems = node.xpathEval('client')
        if len(client_elems) > 0:
            name = client_elems[0].prop("name")
            version = client_elems[0].prop("version")
            update_usage(r_id, name + " " + version)


######################################################################
#{ HTML-Farben
######################################################################

def invert(color):
    """Invertiert eine Hex-Farbe

    @type color: C{StringType}
    @rtype: C{StringType}
    @raise ValueError: keine Hex-Farbe
    """
    
    if color[0] == '#':
        red   = ("0" + hex(255 - int(color[1:3], 16))[2:4])[-2:]
        green = ("0" + hex(255 - int(color[3:5], 16))[2:4])[-2:]
        blue  = ("0" + hex(255 - int(color[5:7], 16))[2:4])[-2:]
        return '#' + red + green + blue
    else:
        raise ValueError(color)

def brightness(color):
    """Helligkeit einer HEX-Farbe

    Maximum ist 255 und bei 125 sollte der Uebergang sein

    @type color: C{StringType}
    @return: Schwarz oder Weiss
    @rtype: C{IntType}
    @raise ValueError: keine Hex-Farbe
    """
    
    if color[0] == '#':
        red   = int(color[1:3], 16)
        green = int(color[3:5], 16)
        blue  = int(color[5:7], 16)
        # from http://www.w3.org/WAI/ER/WD-AERT/#color-contrast
        return (red*299 + green*587 + blue*114) / 1000
    elif color == "red":
        return 76
    elif color == "green":
        return 75
    elif color == "black":
        return 0
    elif color == "white":
        return 255
    else:
        raise ValueError(color)

def color_diff(color1, color2):
    """Unterschied zwischen zwei Farben.
    
    Maximum ist 765 und 500 sollte als Kontrast sein.

    @type color1: C{StringType}
    @type color2: C{StringType}
    @rtype: C{IntType}
    @raise ValueError: keine Hex-Farbe
    """
    
    if color[0] == '#':
        red1   = int(color1[1:3], 16)
        green1 = int(color1[3:5], 16)
        blue1  = int(color1[5:7], 16)
        red2   = int(color2[1:3], 16)
        green2 = int(color2[3:5], 16)
        blue2  = int(color2[5:7], 16)
        red_diff   = ( max(red1, red2) - min(red1, red2) )
        green_diff = ( max(green1, green2) - min(green1, green2) )
        blue_diff  = ( max(blue1, blue2) - min(blue1, blue2) )
        return red_diff + green_diff + blue_diff
    else:
        raise ValueError(color)


# vim:set shiftwidth=4 expandtab smarttab:
