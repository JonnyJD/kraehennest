#!/usr/bin/env python
"""Armeedaten einlesen und ausgeben"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import rbdb
import util
import re
from datetime import datetime, timedelta

from feld import Feld
from reich import get_ritter_id_form
import reich
from user import User
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
    """Uebersetzt ein Schiffsbild in einen Schiffstyp (in UTF)

    (Beim der eigenen Armeen sieht man nur das Bild, nicht die Typbezeichnung.)
    
    @param img: Schiffsbild aus dem Spiel
    @type img: C{StringType}
    @return: Schiffstyp aus dem Spiel
    @rtype: C{StringType}
    """
    # UTF statt html entities, da es direkt in die DB gehen soll
    dictionary = {'s8_1k': "Flo\xC3\x9F", 's8_2k': "Fischerboot",
            's8_3k': "Pinasse", 's8_4k': "Kutter", 's8_5k': "Ketch",
            's8_6k': "Kogge", 's8_7k': "Karavelle", 's8_8k': "Karacke",
            's8_9k': "Galeone", 's8_10k': "Brigg", 's8_11k': "Korvette",
            's8_12k': "Fregatte"}
    if img in dictionary:
        return dictionary[img]
    else:
        return img


class Armee(Feld):
    """Eine Klasse um Armeedaten ein- und auszulesen.  
    """

    def __init__(self, h_id=None):
        """Stellt eine Datenbankverbindung her und initialisiert.

        Bei Eingabe iner h_id wird eine Armeeinstanz eingelesen
        @param h_id: Armee-ID
        @type h_id: C{IntType}
        """

        if h_id is None:
            Feld.__init__(self)
            self.table_name = "armeen"
            self.__entry_name_is_db_name = []
            self.__cols_gathered = False
            self.__int_columns = []
            self.__inactive_entries = []
            self.cond_clause = " AND active = 1"
            self.cond_clause += " AND last_seen >= DATE_SUB(now()"
            self.cond_clause += ", interval 30 hour)"
            if not config.allow_armeen_all():
                if config.allow_armeen_own():
                    self.cond_clause += " AND r_id IN (172, 174, %d)" % (
                                        config.get_user_r_id() )
                else:
                    self.cond_clause += " AND FALSE"

        else:
            self.id = h_id
            """ID der Armee
            @type: C{IntType}
            """
            cols = ["active", "status", "level", "x", "y"]
            cols += ["ritternr", "allicolor", "rittername"]
            cols += ["img", "name", "last_seen"]
            cols += ["strength", "size", "ruf", "bp", "max_bp", "ap", "max_ap"]
            cols += ["schiffstyp"]
            sql = "SELECT " + ", ".join(cols)
            sql += " FROM armeen"
            sql += " LEFT JOIN ritter ON armeen.r_id = ritternr"
            sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
            sql += " WHERE h_id = %s"
            row = util.get_sql_row(sql, h_id)
            if row is None:
                raise KeyError(h_id)
            else:
                self.__table = self.__list(cols, [row])
                self.owner = row[5]
                """ID des Besitzers der Armee
                @type: C{IntType}
                """
                self.owner_name = row[7]
                """Name des besitzenden Ritters
                @type: C{StringType}
                """
                self.name = row[9]
                """Name der Armee
                @type: C{StringType}
                """

    def show(self):
        """Zeigt die Armee in einer L{Tabelle<ausgabe.Tabelle>}
        """
        self.__table.show()

    def delete(self):
        """L&ouml;scht die Armee sofern ein Admin eingeloggt ist
        """

        if config.is_admin():
            sql = "DELETE FROM armeen WHERE h_id = %s"
            if util.sql_execute(sql, self.id) > 0:
                ausgabe.print_important("wurde gel&ouml;scht")
            else:
                ausgabe.print_important("wurde nicht gel&ouml;scht")
        else:
            ausgabe.print_important("darf nur der Admin l&ouml;schen")

    def free(self):
        """Befreit die Armee vom Besitzer sofern ein Admin eingeloggt ist
        """

        if config.is_admin():
            sql = "UPDATE armeen"
            sql += " SET active = 0, status = '" + S_SOLD + "', r_id = NULL"
            sql += ", size = NULL, strength = NULL, ap = NULL, bp = NULL"
            sql += " WHERE h_id = %s"
            if util.sql_execute(sql, self.id) > 0:
                ausgabe.print_important("wurde freigegeben")
            else:
                ausgabe.print_important("wurde nicht freigegeben")
        else:
            ausgabe.print_important("darf nur der Admin freigegeben")

    def deactivate(self):
        """Deaktiviert die Armee, also zeigt sie nicht mehr auf der Karte
        """

        if config.is_kraehe() or self.owner == User().r_id:
            sql = "UPDATE armeen"
            sql += " SET active = 0"
            sql += " WHERE h_id = %s"
            if util.sql_execute(sql, self.id) > 0:
                ausgabe.print_important("wurde deaktiviert")
            else:
                ausgabe.print_important("wurde nicht deaktiviert")
        else:
            ausgabe.print_important("darf nur der Admin deaktivieren")


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
            try:
                if entry[key][0] == "-":
                    ret = len(entry[key]) <= length + 1
                else:
                    ret = len(entry[key]) <= length
                entry[key] = int(entry[key])
            except ValueError, e:
                ret = False
        else:
            # wie lange waere der String in der Datenbank (latin1)
            try:
                l = len(unicode(entry[key],'utf-8').encode('latin-1'))
                ret = l <= length
            except UnicodeEncodeError:
                # solche nicht-latin Unicode Strings landen trotzdem
                # problemlos in der DB Oo
                ret = len(entry[key]) <= length
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

    def __armeen_ohne_ids(self, x, y):
        """Listet die Armeen ohne bekannte IDs als sql_string, args

        @param x: X-Koordinate
        @param y: Y-Koordinate
        @rtype: C{StringType}, C{ArgList}
        """

        sqllist = []
        args = ()
        i = 0
        new = self.new_entries
        while i < len(new):
            if ("h_id" not in new[i] and "r_id" in new[i]
                    and new[i]["x"] == x and new[i]["y"] == y):
                # in genau diesem Fall wollen wir das deaktivieren verhindern
                sqllist.append("(name <> %s OR img <> %s OR r_id <> %s)")
                args += new[i]["name"], new[i]["img"], new[i]["r_id"]
                # danach werden diese Armeen ohne IDs nicht weiter verarbeitet
                del new[i]
            else:
                i += 1
        if len(sqllist) > 0:
            sql_string = " AND " + " AND ".join(sqllist)
            return sql_string, args
        else:
            return "", ()

    def __deactivate(self, sender_id):
        """Deaktiviert alle Armeen in der inactive Liste.
        
        Gibt die Anzahl der deaktivierten Armeen zurueck.
        Die Werte werden NICHT alle zurueckgesetzt.
        Dies ermoeglicht es zuletzt gesehene Werte noch einzusehen.

        @param sender_id: Sendendes Reich
        @rtype: C{IntType}
        """

        if len(self.__inactive_entries) > 0:
            sql = "UPDATE armeen SET active=0 WHERE "
            sqllist = []
            args = ()
            for entry in self.__inactive_entries:
                sql2 = "(level=%s AND x=%s AND y=%s"
                # Armeen ohne IDs die aber mit name,img und r_id passen
                # sollen nicht deaktiviert werden.
                sql_ohne, args_ohne = self.__armeen_ohne_ids(
                        entry["x"], entry["y"])
                sql2 += sql_ohne + ")"
                sqllist.append(sql2);
                args += entry["level"], entry["x"], entry["y"]
                args += args_ohne
            
            sql += "(" + " OR ".join(sqllist) + ") AND "
            if "sicht_versteckt" not in entry:
                # versteckte Armeen nicht deaktivieren
                sql += "( (status is null OR status <> '" + S_HIDDEN + "')"
                # es sei denn sie gehoeren einem selbst
                if sender_id is not None:
                    sql += " OR r_id = %s )"
                    args += sender_id,
                else:
                    sql += " OR FALSE )"
            elif sender_id is not None:
                sql += "r_id = %s"
                args += sender_id,
            else:
                sql += "FALSE"

            # die hier anwesenden Armeen (mit ID) auch nicht erst deaktivieren
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
            elif "h_id" not in new[i]:
                print "Konnte eine Armee nicht identifizieren!<br/>"
                del new[i]
                i -= 1

            i += 1


    def __update(self, entry, sender_id):
        """Datenbank mit Daten aus einem Eintrag aktualisieren

        Gibt den Erfolgsstatus zurueck
        @param entry: Zu pruefender Eintrag
        @type entry: C{Dict}
        @param sender_id: Sendendes Reich
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

        # Aktivitaet und Status korrekt setzen
        if "pos" in entry and entry["pos"] == "taverne":
            entry["update_self"] = True #: hier auch versteckte freigeben
            sqllist.append("active=0")
            sqllist.append("status='" + S_SOLD + "'")
        elif "status" in entry and entry["status"] == S_HIDDEN:
            sqllist.append("active=1")
            sqllist.append("status='" + S_HIDDEN + "'")
        elif "update_self" in entry:
            # ist selbst sichtende Armee und meldet "hidden" nicht
            sqllist.append("active=1")
            sqllist.append("status=NULL")
        else:
            sqllist.append("active=1")
            if sender_id is not None:
                if int(entry["r_id"]) != int(sender_id):
                    # nur fremde sichtbare Armeen sind sicher nicht versteckt
                    # zzgl. zu obigen mit update_self und not hidden
                    sqllist.append("status=NULL")

        # Sonderbehandlung von Monstern mit veraendertem Standort
        if entry["r_id"] == 174 and "strength" not in entry:
            sql2 = "SELECT level, x, y FROM armeen"
            sql2 += " WHERE h_id = %s"
            row = util.get_sql_row(sql2, (entry["h_id"]))
            if (row[0] != entry["level"] or
                    row[1] != entry["x"] or row[2] != entry["y"]):
                # Monster ist an neuem Ort respawned: Werte resetten
                for key in ["size", "Strength"]:
                    sqllist.append(key + "=NULL")

        sql += ", ".join(sqllist)
        sql += " WHERE h_id = %s"
        args += entry["h_id"],
        updated = self.try_execute_safe_secondary(sql, args)

        # entferne den versteckt-status auch, wenn sich die Position aendert
        if "x" in entry and "y" in entry:
            sql = "UPDATE armeen SET status=NULL"
            sql += " WHERE h_id = %s"
            args = (entry["h_id"],)
            sql += " AND (x IS NULL OR x <> %s OR y IS NULL OR y <> %s )"
            args += entry["x"], entry["y"]
            updated += self.try_execute_safe_secondary(sql, args)

        return updated


    def __check_old(self, sender_id):
        """Gleicht die einzufuegenden Armeen mit in der DB vorhandenen ab.
        
        Identische Eintragungen werden aus der TODO-Liste entnommen
        und Aenderungen werden sofort ausgefuehrt.

        Gibt die Anzahl der aktualisierten Armeen zurueck.
        @param sender_id: Sendendes Reich
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
                        if self.__update(new[i], sender_id):
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


    def exec_queue(self, sender_id):
        """Die TODO-Liste wird abgearbeitet.

        Die Eintraege werden als Aktualisierung oder Anfuegung
        der Datenbank hinzugefuegt.
        Es wird geprueft ob Eintraege nicht schon in der Datenbank sind.

        Die Anzahl der deaktivierten, aktualisierten und der neuen Eintraege
        wird zurueckgegeben.
        @param sender_id: Sendendes Reich
        @rtype: C{IntType}, C{IntType}, C{IntType}
        """

        self.__get_ritter_ids()
        self.__get_held_ids()
        # setze alle Armeen die im Sichtbereich waeren auf inaktiv
        inactive_count = self.__deactivate(sender_id)
        update_count = self.__check_old(sender_id)
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
        sql += ", name, ap, bp, schiffstyp, inaktiv"
        sql += " FROM armeen"
        sql += " JOIN ritter ON r_id = ritternr"
        sql += " LEFT JOIN allis ON ritter.alli = allinr"
        sql += " WHERE level='" + self.level + "'"
        sql += self.crop_clause
        sql += self.cond_clause
        sql += self.add_cond
        sql += " ORDER BY allicolor"
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            while row != None:
                entry = dict()
                if row[2] == 174:
                    entry["allyfarbe"] = '#00A000'
                elif row[2] in config.marked_reiche:
                    entry["allyfarbe"] = config.marked_reiche_color
                elif row[11] == reich.S_INAKTIV and config.is_kraehe():
                    entry["allyfarbe"] = "#00A000"
                elif row[11] == reich.S_SCHUTZ and config.is_kraehe():
                    entry["allyfarbe"] = "white"
                elif row[3] is None:
                    # unknown allis are standard link color (no color given)
                    entry["allyfarbe"] = "#FFCC00"   # yellowish
                else: 
                    entry["allyfarbe"] = row[3]
                entry["rittername"] = row[4]
                entry["size"] = row[5]
                entry["strength"] = row[6]
                entry["name"] = row[7]
                entry["ap"] = row[8]
                entry["bp"] = row[9]
                entry["schiffstyp"] = row[10]
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

        # erkenne aktuellen Benutzer
        user = User()
        tabelle = ausgabe.Tabelle()
        secondary = ["ruf", "max_bp", "max_ap"]
        virtual = ["ritternr", "allicolor", "max_dauer"]
        for i in range(0,len(cols)):
            if cols[i] == "size" and cols[i+1] == "ruf":
                tabelle.addColumn(translate(cols[i]), 3)
            elif cols[i] == "bp" and cols[i+1] == "max_bp":
                tabelle.addColumn(translate(cols[i]), 3)
            elif cols[i] == "ap" and cols[i+1] == "max_ap":
                tabelle.addColumn(translate(cols[i]), 3)
            elif cols[i] == "h_id":
                tabelle.addColumn("Admin")
            elif cols[i] not in virtual + secondary:
                tabelle.addColumn(translate(cols[i]))
        for armee in armeen:
            line = []
            armee = ausgabe.escape_row(armee)
            for i in range(0, len(armee)):
                if cols[i] == "active":
                    active = armee[i]
                    if active == 1:
                        line.append("Ja")
                    else:
                        line.append('<div style="color:red">Nein</div>')
                elif cols[i] == "x" and armee[i] != None:
                    link = "/show/feld/" + str(armee[i]) + "." + str(armee[i+1])
                    if armee[i-1] and armee[i-1] != "N":
                        link += "/" + armee[i-1]
                    line.append(ausgabe.link(link, armee[i]))
                elif cols[i] == "y" and armee[i] != None:
                    link = "/show/feld/" + str(armee[i-1]) + "." + str(armee[i])
                    if armee[i-2] and armee[i-2] != "N":
                        link += "/" + armee[i-2]
                    line.append(ausgabe.link(link, armee[i]))
                elif cols[i] == "img":
                    line.append('<img src="/img/armee/' + armee[i] + '.gif" />')
                elif cols[i] == "ritternr":
                    ritter = armee[i]
                    # nachfolgenden Ritternamen verlinken
                    url = "/show/reich/" + str(ritter)
                    if cols[i+1] == "allicolor":
                        if ritter is None:
                            link = "(nicht existent)"
                        else:
                            link = ausgabe.link(url, armee[i+2], armee[i+1])
                        line.append(link)
                    elif cols[i+1] == "rittername":
                        link = ausgabe.link(url, armee[i+1])
                        line.append(link)
                elif cols[i] == "last_seen" and armee[i] != None:
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
                elif cols[i] == "h_id":
                    if (config.is_kraehe() or user.r_id == ritter):
                        url = "/deactivate/armee/" + str(armee[i])
                        cell = '<span style="font-size:8pt;">'
                        deact_string = "[deact]"
                        if active:
                            cell += ausgabe.link(url, deact_string)
                        else:
                            cell += '<span style="color:gray;">'
                            cell += deact_string + '</span>'
                        cell += "&nbsp;"
                        if armee[i+1] is None: # keine max_dauer
                            url = "/delete/armee/" + str(armee[i])
                            cell += ausgabe.link(url, "[del]")
                            cell += "&nbsp;"
                        else:
                            url = "/free/armee/" + str(armee[i])
                            cell += ausgabe.link(url, "[free]")
                        cell += '</span>'
                    else:
                        cell = "id: " + str(armee[i])
                    line.append(cell)
                elif cols[i-1] in ["ritternr", "allicolor"]:
                    # rittername wurde schon abgehakt
                    pass
                elif cols[i] not in virtual:
                    line.append(armee[i])
            tabelle.addLine(line)
        return tabelle

    def list_by_feld(self, level, x, y):
        """Holt alle Armeen auf einem Feld
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["active", "status", "ritternr", "allicolor", "rittername"]
        cols += ["img", "name", "last_seen"]
        cols += ["strength", "size", "ruf", "bp", "max_bp", "ap", "max_ap"]
        cols += ["schiffstyp"]
        cols += ["h_id", "max_dauer"] # zum admin.
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE level = %s AND x = %s AND y = %s"
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

        cols = ["active", "status", "level", "x", "y", "img", "name"]
        cols += ["last_seen"]
        cols += ["strength", "size", "ruf", "bp", "max_bp", "ap", "max_ap"]
        cols += ["schiffstyp"]
        cols += ["ritternr", "h_id", "max_dauer"] # zum admin.
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
        """Holt alle Armeen einer Allianz mit a_id
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = []
        if a_id != -1:
            cols.append("active")
        cols += ["status", "level", "x", "y", "ritternr"]
        if a_id == -1:
            cols.append("allicolor")
        cols += ["rittername", "name", "last_seen"]
        cols += ["strength", "size", "bp", "ap", "schiffstyp"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
        if a_id == -1:
            sql += " WHERE active = 1"
            sql += " AND last_seen >= DATE_SUB(now(), interval 30 hour)"
        else:
            sql += " WHERE allinr = %s"
        sql += " ORDER BY active DESC, last_seen DESC"
        sql += ", allicolor, rittername, x, y, name"
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

    def process_xml(self, node, sender_id):
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
        elif sicht in ["armee", "versteckt"]:
            # alle Armeen die gleiche Position, deshalb die 1. nehmen
            position = node.xpathEval('armee/position')[0] 
            entry = dict()
            if sicht == "versteckt":
                entry["sicht_versteckt"] = True
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
                    if entry["level"] == "U100":
                        print "Das Jagdlevel wird ignoriert.<br />"
                        continue
                    entry["x"] = positions[0].prop("x")
                    entry["y"] = positions[0].prop("y")
                else:
                    entry["pos"] = positions[0].getContent()
                    if entry["pos"] == "taverne":
                        entry["r_id"] = None
                        entry["size"] = None
                        entry["strength"] = None
                        entry["ap"] = None
                        entry["bp"] = None
            entry["img"] = armee.xpathEval('bild')[0].getContent()
            entry["name"] = armee.xpathEval('held')[0].getContent()
            ritter_elems = armee.xpathEval('ritter')
            if len(ritter_elems) > 0:
                if ritter_elems[0].hasProp("r_id"):
                    entry["r_id"] = ritter_elems[0].prop("r_id")
                    # muss dann die aktuelle eigene Armee sein
                    entry["update_self"] = True
                    if sicht in ["keine", "versteckt"]:
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
                strength = strengths[0].prop("now")
                if "?" not in str(strength):
                    entry["strength"] = strength
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
        inactive, updated, added = self.exec_queue(sender_id)
        if (inactive + updated + added) > 0:
            print "Es wurden", inactive, "Armeen deaktiviert,",
            print updated, "aktualisiert und",
            print added, "neu hinzugef&uuml;gt.", "<br />"
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
    elif "action" in form:
        try:
            if "confirmation" in form and form["confirmation"].value=="yes":
                confirmation = True
            else:
                confirmation = False

            # das nur bei Armeen, aber mehr gibt es auch vorerst nicht
            h_id = form["id"].value
            armee = Armee(h_id)
            user = User()
            if ((config.is_kraehe() or user.r_id == armee.owner)
			    and form["action"].value == "deactivate"):
                # Hier ist keine Konfirmation noetig
                armee.deactivate()
                ausgabe.redirect("/show/reich/" + str(armee.owner), 303)
            elif config.is_admin() and form["action"].value == "free":
                ausgabe.print_header("Armee " + h_id + " freigeben")
                armee.show()
                url = "/free/armee/" + str(h_id)
                if confirmation and ausgabe.test_referer(url):
                    armee.free()
                else:
                    message = "Wollen sie diese Armee wirklich freigeben?"
                    url += "/yes"
                    ausgabe.confirmation(message, url)
            elif config.is_admin() and form["action"].value == "delete":
                url = "/delete/armee/" + str(h_id)
                if confirmation and ausgabe.test_referer(url):
                    armee.delete()
                    if armee.owner != None:
                        ausgabe.redirect("/show/reich/" + str(armee.owner), 303)
                    else:
                        ausgabe.redirect("/delete", 303)
                else:
                    ausgabe.print_header("Armee " + h_id + " l&ouml;schen")
                    armee.show()
                    message = "Wollen sie diese Armee wirklich l&ouml;schen?"
                    url += "/yes"
                    ausgabe.confirmation(message, url)
            else:
                action = form["action"].value
                message = "Werde " + action + " nicht ausf&uuml;hren!"
                ausgabe.print_header(message)
        except KeyError, e:
            ausgabe.print_header("Unbekannte Armee: " + e.args[0])
    else:
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
