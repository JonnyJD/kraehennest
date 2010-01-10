#!/usr/bin/python
"""Armeedaten einlesen und ausgeben"""

#import cgitb
#cgitb.enable()

import rbdb
import util
import re
from datetime import datetime, timedelta
from feld import Feld
from reich import get_ritter_id_form
import ausgabe

# Armeestati
S_SOLD = 'S'    #: Taverne
S_HIDDEN = 'H'  #: versteckt
S_QUEST = 'Q'   #: Quest
S_DEAD = 'D'    #: tot

def status_string(status):
    """Gibt einen String fuer einen Armeestatus zurueck
    
    @param status: Status Character aus der Datenbank
    @type status: C{StringType}
    @rtype: C{StringType}
    """
    return {S_SOLD: "Taverne", S_HIDDEN: "versteckt",
            S_QUEST: "Quest", S_DEAD: "tot", None: None}[status]

def translate(column):
    """Uebersetzt den Datenbanknamen fuer die Anzeige
    
    @param column: Name in der Datenbank (oder Variable)
    @return: Anzeigename (mit HTML entities)
    @rtype: C{StringType}
    """
    dictionary = {'strength': "St&auml;rke", 'size': "Gr&ouml;&szlig;e",
            'active': "da?", 'level': "Lvl", 'last_seen': "zuletzt gesehen",
            'bp': "BP", 'ap': "AP"}
    if column in dictionary:
        return dictionary[column]
    else:
        return column.capitalize()

def schiffstyp(img):
    """Uebersetzt ein Schiffsbild in einen Schiffstyp

    (Beim der eigenen Armeen sieht man nur das Bild, nicht die Typbezeichnung.)
    
    @param img: Schiffsbild aus dem Spiel
    @type img: C{StringType}
    @return: Schiffstyp aus dem Spiel
    @rtype: C{StringType}
    """
    dictionary = {'s8_1k': "Flo&szlig;", 's8_2k': "Fischerboot",
            's8_3k': "Pinasse", 's8_4k': "Kutter", 's8_5k': "Ketch",
            's8_6k': "Kogge", 's8_7k': "Karavelle", 's8_8k': "Karacke",
            's8_9k': "Galeone", 's8_10k': "Brigg", 's8_11k': "Korvette",
            's8_12k': "Fregatte"}
    if column in dictionary:
        return dictionary[img]
    else:
        return column


class Armee(Feld):
    """Eine Klasse um Armeedaten ein- und auszulesen.  
    """

    def __init__(self):
        """Stellt eine Datenbankverbindung her und initialisiert.
        """
        Feld.__init__(self)
        self.table_name = "armeen"
        self.__entry_name_is_db_name = []
        self.__cols_gathered = False
        self.__int_columns = []
        self.__inactive_entries = []

    def __is(self, is_int, entry, mandatory, db_col, key, length):
        """Prueft einen Wert  auf korrekten Typ.

        Des Weiteren wird die Liste der Datenbankfelder gefuellt
        @param is_int: Ob es ein Integer sein soll
        @type is_int: C{BooleanType}
        @param entry: Eintraege
        @type entry: C{Dict}
        @param mandatory: Ob es zwinged gefuellt sein muss
        @type mandatory: C{BooleanType}
        @param db_col: Ob es unter dem Namen in der Datenbank vorkommt
        @type db_col: C{BooleanType}
        @param key: Welcher Teil des Eintrags geprueft werden soll
        @type key: C{StringType}
        @param length: Die maximale Laenge
        @type length: C{IntType}
        @rtype: C{BooleanType}
        """

        if db_col and not self.__cols_gathered:
            self.__entry_name_is_db_name.append(key)
        if key not in entry or entry[key] == None:
            ret = mandatory == False
        elif is_int:
            ret = re.match('-?[0-9]+$',entry[key]) and len(entry[key]) <= length
            # after the length check we can make it integer
            entry[key] = int(entry[key])
        else:
            # wie lange waere der String in der Datenbank (latin1)
            ret = len(unicode(entry[key],'utf-8').encode('latin-1')) <= length
        if not ret:
            print entry[key], "ist nicht zul&auml;ssig als", key, "<br />"
        return ret

    def __check_entry(self, entry):
        """Prueft alle Werte im Eintrag auf korrekten Typ.

        Des Weiteren wird die Liste der Datenbankfelder gefuellt
        @param entry: Zu pruefender Eintrag
        @type entry: C{Dict}
        @rtype: C{BooleanType}
        """

        # Named Booleans
        MAN     = True;         OPT   = False
        DBCOL   = True;         NO_DB = False
        INT     = True;         STR   = False

        # DBCOL meint, dass es direkt so in die Datenbank gehen wird
        ret =  (self.__is(STR,entry, MAN, DBCOL, "name", 30)
                and self.__is(STR,entry, MAN, DBCOL, "img", 10)
                and self.__is(INT,entry, OPT, DBCOL, "x", 3)
                and self.__is(INT,entry, OPT, DBCOL, "y", 3)
                and self.__is(STR,entry, OPT, DBCOL, "level", 2)
                and self.__is(INT,entry, OPT, DBCOL, "h_id", 8)
                and self.__is(STR,entry, OPT, NO_DB, "status", 1)
                and self.__is(INT,entry, OPT, DBCOL, "r_id", 5)
                and self.__is(STR,entry, OPT, NO_DB, "ritter", 80)
                and self.__is(INT,entry, OPT, DBCOL, "size", 2)
                and self.__is(INT,entry, OPT, DBCOL, "strength", 3)
                and self.__is(INT,entry, OPT, DBCOL, "ruf", 2)
                and self.__is(INT,entry, OPT, DBCOL, "bp", 2)
                and self.__is(INT,entry, OPT, DBCOL, "max_bp", 2)
                and self.__is(INT,entry, OPT, DBCOL, "ap", 2)
                and self.__is(INT,entry, OPT, DBCOL, "max_ap", 2)
                and self.__is(INT,entry, OPT, DBCOL, "dauer", 2)
                and self.__is(INT,entry, OPT, DBCOL, "max_dauer", 2)
                and self.__is(INT,entry, OPT, DBCOL, "t_id", 8)
                and self.__is(STR,entry, OPT, DBCOL, "schiffstyp", 15)
                and self.__is(STR,entry, OPT, DBCOL, "schiffslast", 15)
                and self.__is(INT,entry, OPT, DBCOL, "verlaengerungen", 2)
                )
        self.__cols_gathered = True
        return ret

    def __check_inactive(self, entry):
        """Wie L{__check_entry}, fuer Inaktiveintraege

        @param entry: Zu pruefender Eintrag
        @type entry: C{Dict}
        @rtype: C{BooleanType}
        """

        # Named Booleans
        MAN     = True;         OPT   = False
        DBCOL   = True;         NO_DB = False
        INT     = True;         STR   = False

        return (self.__is(INT, entry, MAN, NO_DB, "x", 3)
                and self.__is(INT,entry, MAN, NO_DB, "y", 3)
                and self.__is(STR,entry, MAN, NO_DB, "level", 2)
                )

    def queue_entry(self, entry):
        """Nimmt eine Armee zum Eintragen erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind.
        @param entry: Zu pruefender Eintrag
        @type entry: C{Dict}
        @rtype: C{BooleanType}
        """

        if self.__check_entry(entry):
            self.new_entries.append(entry)
            return True
        else:
            return False


    def queue_inactive(self, entry):
        """Nimmt eine Armee zum Deaktivieren erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind.
        @param entry: Zu pruefender Eintrag
        @type entry: C{Dict}
        @rtype: C{BooleanType}
        """

        if self.__check_inactive(entry):
            self.__inactive_entries.append(entry)
            return True
        else:
            return False

    def __deactivate(self):
        """Deaktiviert alle Armeen in der inactive Liste.
        
        Gibt die Anzahl der deaktivierten Armeen zurueck
        @rtype: C{IntType}
        """

        if len(self.__inactive_entries) > 0:
            sql = "UPDATE armeen SET active=0 WHERE "
            sqllist = []
            args = ()
            for entry in self.__inactive_entries:
                sqllist.append("(level=%s AND x=%s AND y=%s)")
                args += entry["level"], entry["x"], entry["y"]
            
            sql += "(" + " OR ".join(sqllist) + ") AND "
            # versteckte Armeen nicht deaktivieren
            sql += "(status is null OR status <> '" + S_HIDDEN + "')"
            # die hier anwesenden Armeen garnicht erst deaktivieren
            sqllist = []
            for entry in self.new_entries:
                sqllist.append("h_id<>%s")
                args += entry["h_id"],
            if len(self.new_entries) > 0:
                sql += " AND " + " AND ".join(sqllist)
            self.__inactive_entries = []
            return self.try_execute_safe(sql, args)
        else:
            return 0

    def __get_ritter_ids(self):
        """Holt IDs fuer alle Ritter von denen nur Namen bekannt sind
        """

        sqllist = []
        args = ()
        for entry in self.new_entries:
            if ("r_id" not in entry and "ritter" in entry
                    and entry["ritter"] not in args):
                sqllist.append("rittername=%s")
                args += entry["ritter"],
        if len(sqllist) > 0:
            sql = "SELECT ritternr, rittername FROM ritter WHERE "
            sql += " OR ".join(sqllist)
            self.try_execute_safe(sql, args)
            row = self.cursor.fetchone()
            while row != None:
                for entry in self.new_entries:
                    if "r_id" not in entry and row[1] == entry["ritter"]:
                        entry["r_id"] = int(row[0])
                row = self.cursor.fetchone()
        # entferne entries die immernoch keine r_id haben
        i = 0
        while i < len(self.new_entries):
            if "r_id" not in self.new_entries[i]:
                print "Ritter", self.new_entries[i]["ritter"], "ist unbekannt!"
                print get_ritter_id_form(self.new_entries[i]["ritter"]),"<br />"
                del self.new_entries[i]
            else:
                i += 1

    def __get_held_ids(self):
        """Holt Armee-IDs fuer alle Helden von denen nur Namen bekannt sind
        """

        sqllist = []
        args = ()
        i = 0
        new = self.new_entries
        while i < len(new):
            if ("h_id" not in new[i] and "img" in new[i] and "name" in new[i]):
                sql = "SELECT h_id FROM armeen"
                sql += " WHERE img=%s AND name=%s"
                args = (new[i]["img"], new[i]["name"])
                if self.try_execute_safe(sql, args) == 1:
                    row = self.cursor.fetchone()
                    new[i]["h_id"] = int(row[0])
                else:
                    print "Keine ID fuer", new[i]["name"], "gefunden.<br />"
                    del new[i]
                    i -= 1
            elif "h_id" not in new[i]:
                print "Konnte eine Armee nicht identifizieren!<br/>"
                del new[i]
                i -= 1

            i += 1


    def __update(self, entry):
        """Datenbank mit Daten aus einem Eintrag aktualisieren

        Gibt den Erfolgsstatus zurueck
        @param entry: Zu pruefender Eintrag
        @type entry: C{Dict}
        @rtype: C{BooleanType}
        """

        sql = "UPDATE armeen SET "
        sqllist = []
        args = ()
        for key in self.__entry_name_is_db_name:
            if key in entry:
                sqllist.append(key + "=%s")
                args += entry[key],
        sqllist.append("last_seen=NOW()")
        if "pos" in entry and entry["pos"] == "taverne":
            sqllist.append("active=0")
            sqllist.append("status='" + S_SOLD + "'")
        elif "status" in entry and entry["status"] == S_HIDDEN:
            sqllist.append("active=1")
            sqllist.append("status='" + S_HIDDEN + "'")
        else:
            sqllist.append("active=1")
            sqllist.append("status=NULL")
        sql += ", ".join(sqllist)
        sql += " WHERE h_id = %s"
        args += entry["h_id"],
        if not "update_self" in entry or not entry["update_self"]:
            # versteckte Armeen updaten nur sich selbst
            sql += " AND (status IS NULL OR status <> '" + S_HIDDEN + "')"
        return self.try_execute_safe_secondary(sql, args)


    def __check_old(self):
        """Gleicht die einzufuegenden Armeen mit in der DB vorhandenen ab.
        
        Identische Eintragungen werden aus der TODO-Liste entnommen
        und Aenderungen werden sofort ausgefuehrt.

        Gibt die Anzahl der aktualisierten Armeen zurueck.
        @rtype: C{IntType}
        """

        new = self.new_entries
        num_updated = 0
        if len(new) > 0:
            sql = "SELECT h_id, name FROM armeen WHERE "
            sqllist = []
            args = ()
            for entry in new:
                sqllist.append("h_id=%s")
                args += entry["h_id"],
            sql += " OR ".join(sqllist)
            self.try_execute_safe(sql, args)
            row = self.cursor.fetchone()
            while row != None:
                i = 0
                while i < len(new):
                    if (new[i]["h_id"] == row[0]):
                        if self.__update(new[i]):
                            num_updated += 1
                        del new[i]
                    else:
                        i += 1
                row = self.cursor.fetchone()
        return num_updated


    def __insert(self):
        """Fuegt alle in der TODO-Liste verbliebenen Eintraege in die DB ein.

        Es wird hier davon ausgegangen, dass diese Eintraege
        noch nicht in der Datenbank vorhanden sind.

        Gibt die Anzahl der eingefuegten Armeen zurueck.
        @rtype: C{IntType}
        """

        num_inserted = 0
        for entry in self.new_entries:
            sql = "INSERT INTO armeen ("
            sqlcols = []
            args = ()
            for key in self.__entry_name_is_db_name:
                if key in entry:
                    sqlcols.append(key)
                    args += entry[key],
            if "pos" in entry and entry["pos"] == "taverne":
                sqlcols.append("active");
                args += 0,
                sqlcols.append("status");
                args += S_SOLD,
            elif "status" in entry and entry["status"] == S_HIDDEN:
                sqlcols.append("active");
                args += 1,
                sqlcols.append("status");
                args += S_HIDDEN,
            sql += ", ".join(sqlcols) + ") VALUES ("
            sql += ", ".join(["%s" for i in range(0,len(sqlcols))]) + ")"
            self.new_entries = []
            num_inserted += self.try_execute_safe(sql, args)
        return num_inserted


    def exec_queue(self):
        """Die TODO-Liste wird abgearbeitet.

        Die Eintraege werden als Aktualisierung oder Anfuegung
        der Datenbank hinzugefuegt.
        Es wird geprueft ob Eintraege nicht schon in der Datenbank sind.

        Die Anzahl der deaktivierten, aktualisierten und der neuen Eintraege
        wird zurueckgegeben.
        @rtype: C{IntType}, C{IntType}, C{IntType}
        """

        self.__get_ritter_ids()
        self.__get_held_ids()
        # setze alle Armeen die im Sichtbereich waeren auf inaktiv
        inactive_count = self.__deactivate()
        update_count = self.__check_old()
        insert_count = self.__insert()
        return inactive_count, update_count, insert_count

    def fetch_data(self, level='N',
            xmin=None, xmax=None, ymin=None, ymax=None):
        """Liest die Armeedaten von der Datenbank aus."""

        if level.isalnum() and len(level) <= 2:
            self.level = level
            self.crop(xmin, xmax, ymin, ymax)
            self.get_border()
            self.__get_entries()
        else:
            print "FEHLER: Level '" + level + "' ist ung&uuml;ltig"

    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank.
        
        @rtype: C{BooleanType}"""

        sql = "SELECT x, y, ritternr, allicolor, rittername, size, strength"
        sql += ", name, ap, bp"
        sql += " FROM armeen"
        sql += " JOIN ritter ON r_id = ritternr"
        sql += " JOIN allis ON ritter.alli = allinr"
        sql += " WHERE level='" + self.level + "'"
        sql += " AND active = 1"
        sql += " AND last_seen >= DATE_SUB(now(), interval 30 hour)"
        sql += self.crop_clause
        sql += self.add_cond
        sql += " ORDER BY allicolor"
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            while row != None:
                entry = dict()
                if row[2] == 174:
                    entry["allyfarbe"] = '#00A000'
                else: 
                    entry["allyfarbe"] = row[3]
                entry["rittername"] = row[4]
                entry["size"] = row[5]
                entry["strength"] = row[6]
                entry["name"] = row[7]
                entry["ap"] = row[8]
                entry["bp"] = row[9]
                if (row[0],row[1]) not in self.entries:
                    self.entries[row[0],row[1]] = []
                self.entries[row[0],row[1]].append(entry)
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def __list(self, cols, armeen):
        """Erstellt eine Tabelle aus den Armeen

        @param cols: Die Spaltenueberschriften
        @type cols: C{List} of C{Dict}
        @param armeen: Armeeliste
        @type armeen: C{List} of C{Dict}
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        tabelle = ausgabe.Tabelle()
        virtual = ["ritternr", "allicolor", "ruf", "max_bp", "max_ap"]
        for i in range(0,len(cols)):
            if cols[i] == "size" and cols[i+1] == "ruf":
                tabelle.addColumn(translate(cols[i]), 3)
            elif cols[i] == "bp" and cols[i+1] == "max_bp":
                tabelle.addColumn(translate(cols[i]), 3)
            elif cols[i] == "ap" and cols[i+1] == "max_ap":
                tabelle.addColumn(translate(cols[i]), 3)
            elif cols[i] not in virtual:
                tabelle.addColumn(translate(cols[i]))
        for armee in armeen:
            line = []
            for i in range(0, len(armee)):
                if cols[i] == "active":
                    if armee[i] == 1:
                        line.append("Ja")
                    else:
                        line.append('<div style="color:red">Nein</div>')
                elif cols[i] == "ritternr":
                    # nachfolgenden Ritternamen verlinken
                    url = "/show/reich/" + str(armee[i])
                    if cols[i+1] == "allicolor":
                        if armee[i] == 174: # Keiner
                            link = ausgabe.link(url, armee[i+2], "green")
                        else:
                            link = ausgabe.link(url, armee[i+2], armee[i+1])
                    else:
                        link = ausgabe.link(url, armee[i+1])
                    line.append(link)
                elif cols[i] == "last_seen":
                    string = ausgabe.datetime_delta_string(armee[i])
                    delta = datetime.today() - armee[i]
                    if delta > timedelta(hours=30):
                            zelle = '<div style="color:red">'
                            zelle += string + '</div>'
                            line.append(zelle)
                    elif delta > timedelta(hours=6):
                            zelle = '<div style="color:orange">'
                            zelle += string + '</div>'
                            line.append(zelle)
                    else:
                        line.append(string)
                elif cols[i] in ["ruf", "max_bp", "max_ap"]:
                    line.append("/")
                    if armee[i] is not None:
                        # to_str damit es left aligned wird
                        line.append(str(armee[i]))
                    else:
                        line.append(armee[i])
                elif cols[i] == "status":
                    line.append(status_string(armee[i]))
                elif cols[i-1] not in ["ritternr", "allicolor"]:
                    line.append(armee[i])
            tabelle.addLine(line)
        return tabelle

    def list_by_feld(self, level, x, y):
        """Holt alle Armeen auf einem Feld
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["status", "ritternr", "allicolor", "rittername"]
        cols += ["name", "last_seen"]
        cols += ["strength", "size", "ruf", "bp", "max_bp", "ap", "max_ap"]
        cols += ["schiffstyp"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE level = %s AND x = %s AND y = %s"
        sql += " AND active = 1"
        sql += " AND last_seen >= DATE_SUB(now(), interval 30 hour)"
        sql += " ORDER BY last_seen DESC, allicolor, rittername, name"
        try:
            self.cursor.execute(sql, (level, x, y))
            armeen = self.cursor.fetchall()
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_by_reich(self, r_id):
        """Holt alle Armeen eines Reiches mit r_id

        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["active", "status", "level", "x", "y", "name", "last_seen"]
        cols += ["strength", "size", "ruf", "bp", "max_bp", "ap", "max_ap"]
        cols += ["schiffstyp"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " WHERE r_id = %s"
        sql += " ORDER BY active DESC, last_seen DESC, x, y, name"
        try:
            self.cursor.execute(sql, r_id)
            armeen = self.cursor.fetchall()
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_all(self):
        """Holt alle(!) Armeen

        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """
        return self.list_by_allianz(-1)

    def list_by_allianz(self, a_id):
        """Holt alle Armeen eines Allianz mit a_id
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["status", "level", "x", "y", "ritternr"]
        if a_id == -1:
            cols.append("allicolor")
        cols += ["rittername", "name", "last_seen"]
        cols += ["strength", "size", "bp", "ap", "schiffstyp"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE"
        sql += " active = 1"
        if a_id != -1:
            sql += " AND allinr = %s"
        sql += " AND last_seen >= DATE_SUB(now(), interval 30 hour)"
        sql += " ORDER BY last_seen DESC, allicolor, rittername, x, y, name"
        try:
            if a_id != -1:
                self.cursor.execute(sql, a_id)
            else:
                self.cursor.execute(sql)
            armeen = self.cursor.fetchall()
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def process_xml(self, node):
        """Liest Daten aus einem XML-Dokument ein"""

        sicht = util.get_view_type(node)
        if sicht == "turm":
            # Feldaten gibt es fuer genau die sichtbaren Felder
            felder = node.xpathEval('../felder/feld') 
            for feld in felder:
                entry = dict()
                entry["level"] = feld.prop("level")
                entry["x"] = feld.prop("x");  entry["y"] = feld.prop("y")
                self.queue_inactive(entry)
        elif sicht == "armee":
            # alle Armeen die gleiche Position, deshalb die 1. nehmen
            position = node.xpathEval('armee/position')[0] 
            entry = dict()
            entry["level"] = position.prop("level")
            entry["x"] = position.prop("x"); entry["y"] = position.prop("y")
            self.queue_inactive(entry)

        armeen = node.xpathEval('armee')
        for armee in armeen:
            entry = dict()
            if armee.hasProp("h_id"):
                entry["h_id"] = armee.prop("h_id")
            positions = armee.xpathEval('position')
            if len(positions) > 0:
                if positions[0].hasProp("level"):
                    entry["level"] = positions[0].prop("level")
                    entry["x"] = positions[0].prop("x")
                    entry["y"] = positions[0].prop("y")
                else:
                    entry["pos"] = positions[0].getContent()
                    if entry["pos"] == "taverne":
                        entry["r_id"] = None
            entry["img"] = armee.xpathEval('bild')[0].getContent()
            entry["name"] = armee.xpathEval('held')[0].getContent()
            ritter_elems = armee.xpathEval('ritter')
            if len(ritter_elems) > 0:
                if ritter_elems[0].hasProp("r_id"):
                    entry["r_id"] = ritter_elems[0].prop("r_id")
                    # muss dann die aktuelle eigene Armee sein
                    entry["update_self"] = True
                    if sicht == "keine":
                        # nur sich selbst als versteckt markieren
                        entry["status"] = S_HIDDEN
                else:
                    entry["ritter"] = ritter_elems[0].getContent()
            sizes = armee.xpathEval('size')
            if len(sizes) == 1:
                if sizes[0].hasProp("now"):
                    entry["size"] = sizes[0].prop("now")
                if sizes[0].hasProp("max"):
                    entry["ruf"] = sizes[0].prop("max")
            strengths = armee.xpathEval('strength')
            if len(strengths) == 1:
                entry["strength"] = strengths[0].prop("now")
            bps = armee.xpathEval('bp')
            if len(bps) == 1:
                if bps[0].hasProp("now"):
                    entry["bp"] = bps[0].prop("now")
                if bps[0].hasProp("max"):
                    entry["max_bp"] = bps[0].prop("max")
            aps = armee.xpathEval('ap')
            if len(aps) == 1:
                if aps[0].hasProp("now"):
                    entry["ap"] = aps[0].prop("now")
                if aps[0].hasProp("max"):
                    entry["max_ap"] = aps[0].prop("max")
            schiffe = armee.xpathEval('schiff') 
            if len(schiffe) == 1:
                entry["schiffstyp"] = schiffstyp(schiffe[0].prop("typ"))
                #entry["schiffslast"] = schiffe[0].prop("last")
            else:
                entry["schiffstyp"] = None;
            dauer_elems = armee.xpathEval('dauer')
            if len(dauer_elems) == 1:
                if dauer_elems[0].hasProp("now"):
                    entry["dauer"] = dauer_elems[0].prop("now")
                if dauer_elems[0].hasProp("max"):
                    entry["max_dauer"] = dauer_elems[0].prop("max")
            if not self.queue_entry(entry):
                print entry, "<br />"
                print "enthielt Fehler <br />"
            #else:
            #    print entry, " eingehangen<br />"

        # fuehre updates aus
        inactive, updated, added = self.exec_queue()
        if (inactive + updated + added) > 0:
            print "Es wurden", inactive, "Armeen deaktiviert,",
            print updated, "aktualisiert und",
            print added, "neu hinzugef&auml;gt.", "<br />"
        else:
            print "Keine Armeen ge&auml;ndert.", "<br />"


# Aufruf als Skript
if __name__ == '__main__':
    import cgi
    form = cgi.FieldStorage()

    if "list" in form:
        ausgabe.print_header("Armeeliste")

        armee = Armee()
        armeetabelle = armee.list_all()
        print "Anzahl Armeen:", armeetabelle.length()
        armeetabelle.show()
    else:
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
