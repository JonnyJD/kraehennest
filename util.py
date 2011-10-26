"""Einige kleine Hilfsfunktionen"""

import datetime
import time
import email.Utils # damit es auch vor python 2.5 geht
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
    day = int(datum[0])
    if len(datum) == 3:
        month = int(datum[1])
        year = int(datum[2])
    else:
        name = datum[1].split()[0]
        if name == "Eor":       month = 1
        elif name == "Lunat":   month = 2
        elif name == "Karim":   month = 3
        elif name == "Raziel":  month = 4
        elif name == "Silva":   month = 5
        elif name == "Atius":   month = 6
        elif name == "Rea":     month = 7
        elif name == "Malkar":  month = 8
        elif name == "Lokia":   month = 9
        elif name == "Azarath": month = 10
        elif name == "Eloria":  month = 11
        elif name == "Lymena":  month = 12
        else:
            print "Monat '" + name + "' ist unbekannt!<br />"
        year = int(datum[1].split()[1])
    year += 1653

    return datetime.date(year, month, day)

def print_error_message(message, floating=False):
    """Gibt eine hervorstechende HTML-Fehlermeldung aus
    
    @param message: Auszugebende Nachricht
    @type message: C{StringType}
    @param floating: Ob die Nachricht in eine mitlaufende Box soll
    @type floating: C{BooleanType}
    """

    print '<div style="'
    if floating:
        print 'position:relative; z-index:99;'
        print ' left:70px; top:25px; max-width:730px; padding:3px;'
    print ' color:red; background-color:black;">'
    print message
    print '</div>'


######################################################################
#{ SQL
######################################################################

def try_execute_safe(cursor, sql, args=()):
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

def get_sql_row(sql, args=()):
    """Fuehrt eine Datenbankabfrage aus

    @return: Gewonnene Zeile
    @rtype: C{List}
    """
    conn = rbdb.connect()
    cursor = conn.cursor()
    try_execute_safe(cursor, sql, args)
    row = cursor.fetchone()
    conn.close()
    return row

def get_sql_rows(sql, args=()):
    """Fuehrt eine Datenbankabfrage aus

    @return: Gewonnene Tabelle
    @rtype: C{List}
    """
    conn = rbdb.connect()
    cursor = conn.cursor()
    try_execute_safe(cursor, sql, args)
    rows = cursor.fetchall()
    conn.close()
    return rows

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


def map_last_modified(allow_doerfer=True, allow_armeen=True):
    """Bestimmt das letzte Aenderungsdatum der Karte.
    Es wird bedacht ob Aenderungen von Armeen,
    oder Doerfern ueberhaupt relevant sind.

    @return: Aenderungsdatum
    @rtype: C{datetime}
    """
    row = get_sql_row("show table status from rb like 'armeen'")
    last_update_armeen = row[12] # Update_time
    row = get_sql_row("show table status from rb like 'dorf'")
    last_update_doerfer = row[12] # Update_time
    row = get_sql_row("show table status from rb like 'felder'")
    last_update_felder = row[12] # Update_time
    last_update = last_update_felder
    if allow_armeen and last_update < last_update_armeen:
        last_update = last_update_armeen
    if allow_doerfer and last_update < last_update_doerfer:
        last_update = last_update_doerfer
    return last_update

def map_last_modified_tuple(allow_doerfer=True, allow_armeen=True):
    """Bestimmt das letzte Aenderungsdatum als Tupel
    Es wird bedacht ob Aenderungen von Armeen,
    oder Doerfern ueberhaupt relevant sind.

    @return: Aenderungsdatum
    @rtype: C{struct_time}
    """
    last_modified = map_last_modified(allow_doerfer, allow_armeen)
    return last_modified.timetuple()

def map_last_modified_http(allow_doerfer=True, allow_armeen=True):
    """Bestimmt das letzte Aenderungsdatum der Karte im HTTP Format
    Es wird bedacht ob Aenderungen von Armeen,
    oder Doerfern ueberhaupt relevant sind.

    @return: Aenderungsdatum
    @rtype: C{String}
    """
    time_tuple = map_last_modified_tuple(allow_doerfer, allow_armeen)
    time_float = time.mktime(time_tuple)
    return email.Utils.formatdate(time_float, localtime=False, usegmt=True)


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
        return r_id
    else:
        return None

def last_sent(account=None):
    """Gibt die Zeit wann das zugehoerige Reich zuletzt Daten gesendet hat
    
    @param account: der Kraehenserveraccount
    @type account: C{StringType}
    @return: Datum der letzten empfangenen Aktualisierung
    @rtype: C{datetime.date}
    """

    sql = "SELECT max(last_seen) FROM versionen"
    if account == None:
        sql += " WHERE 0"
        args = ()
    else:
        sql += " WHERE username = %s"
        args = (account)
    try:
        conn = rbdb.connect()
        cursor = conn.cursor()
        cursor.execute(sql, args)
        row = cursor.fetchone()
        if row == None:
            # garnicht in der Tabelle -> garkein Zugriffsrecht
            return None
        else:
            return row[0]
    except rbdb.Error, e:
        util.print_html_error(e)
        return None

def get_user_r_id(username):
    """Gebe die zugeordnete Reichsid eines Benutzers zurueck.

    @rtype: C{IntType}
    """
    sql = "SELECT r_id from versionen where username=%s"
    row = get_sql_row(sql, username)
    if row:
        return row[0]
    else:
        return 0


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
    @raise ValueError: keine Hex-Farben
    """
    
    if color1[0] == '#' and color2[0] == '#':
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

def hex_byte(int):
    """Gibt einen 2 hex char String fuer einen Integer.
    @type int: C{IntType}
    @rtype: C{StringType}
    """
    if int < 16:
        return '0' + hex(int)[2:]
    else:
        return hex(int)[2:]

def color_shade(color1, color2, shade):
    """Schattiere eine Farbe mit einer zweiten.
    
    @param color1: Hauptfarbe
    @type color1: C{StringType}
    @param color2: Schattierungsfarbe
    @type color2: C{StringType}
    @param shade: 0 -> Farbe1 voll; 1 -> Farbe2 voll;
    @type shade: C{FloatType}
    @rtype: C{IntType}
    @raise ValueError: keine Hex-Farben
    """
    
    if color1[0] == '#' and color2[0] == '#':
        red1   = int(color1[1:3], 16)
        green1 = int(color1[3:5], 16)
        blue1  = int(color1[5:7], 16)
        red2   = int(color2[1:3], 16)
        green2 = int(color2[3:5], 16)
        blue2  = int(color2[5:7], 16)
        red = int(red1 + shade * (red2 - red1))
        green = int(green1 + shade * (green2 - green1))
        blue = int(blue1 + shade * (blue2 - blue1))
        return '#' + hex_byte(red) + hex_byte(green) + hex_byte(blue)
    else:
        raise ValueError(color)


# vim:set shiftwidth=4 expandtab smarttab:
