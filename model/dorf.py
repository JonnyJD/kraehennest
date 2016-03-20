#!/usr/bin/env python
"""Dorfdaten"""

import re
from datetime import date, timedelta

import config
import rbdb
import util
import ausgabe

from feld import Feld
import reich


def translate(column):
    """Uebersetzt den Datenbanknamen fuer die Anzeige
    
    @param column: Name in der Datenbank (oder Variable)
    @return: Anzeigename (mit HTML entities)
    @rtype: C{StringType}
    """
    dictionary = {'aktdatum': "zuletzt gesehen"}
    if column in dictionary:
        return dictionary[column]
    else:
        return column.capitalize()


class Dorf(Feld):
    """Eine Klasse um Dorfdaten ein- und auszulesen.  
    """

    def __init__(self):
        """Stellt eine Datenbankverbndung her und initialisiert.
        """

        Feld.__init__(self)
        self.table_name = "dorf"
        self.__entry_name_is_db_name = []
        self.__cols_gathered = False
        self.__empty_entries = []

    def fetch_data(self,
            xmin=None, xmax=None, ymin=None, ymax=None):
        """Liest die Terraindaten von der Datenbank aus."""

        self.level = 'N'
        self.crop(xmin, xmax, ymin, ymax)
        self.__get_entries()


    # can't use the generic crop because of "x,y" being 1 field
    def crop(self, xmin, xmax, ymin, ymax):
        """Erstellt die SQL-Bedingung mit der der Bereich festgelegt wird."""

        try:
            clauses = []
            if xmin != None and xmax != None:
                disjunction = []
                for x in range(xmin, xmax + 1):
                    disjunction.append(' koords  LIKE "%d,%%" ' % int(x))
                clauses.append(" OR ".join(disjunction))
            if ymin != None and ymax != None:
                disjunction = []
                for y in range(ymin, ymax + 1):
                    disjunction.append(' koords  LIKE "%%,%d" ' % int(y))
                clauses.append(" OR ".join(disjunction))
            if len(clauses) > 0:
                self.crop_clause = " AND " + " AND ".join(clauses)
        except ValueError:
            print "Die angegebenene Grenzen sind ungueltig <br />"


    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank.
        
        @rtype: C{BooleanType}"""

        sql = """SELECT koords, dorfname, dorflevel, aktdatum, mauer,
                        rittername, allis.alli, alliname, allicolor, inaktiv,
                        dorf.ritternr
                FROM dorf INNER JOIN ritter ON dorf.ritternr= ritter.ritternr
                    LEFT OUTER JOIN allis ON ritter.alli=allis.allinr"""
        # so dass die andere clauses angehangen werden koennen:
        sql += " WHERE 1"
        #sql += " WHERE level='" + self.level + "'"
        sql += self.crop_clause
        sql += self.add_cond
        try:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            is_kraehe = config.is_kraehe()
            for row in rows:
                try:
                    x, y = map(int, row[0].split(","))
                except ValueError:
                    continue
                self.entries[x,y] = {'dorfname': row[1],
                        'dorflevel': row[2], 'aktdatum': row[3],
                        'mauer': row[4], 'rittername': row[5],
                        'alliname': row[7], 'allyfarbe': row[8]}
                if row[5] == "Keiner":
                    self.entries[x,y]["allyfarbe"] = "#00A000"
                elif row[10] in config.marked_reiche:
                    self.entries[x,y]["allyfarbe"] = (
                                        config.marked_reiche_color)
                elif row[9] == reich.S_INAKTIV and is_kraehe:
                    farbe = util.color_shade('#00A000', row[8], 0.3)
                    self.entries[x,y]["allyfarbe"] = farbe
                elif row[9] == reich.S_SCHUTZ:
                    farbe = util.color_shade('#FFFFFF', row[8], 0.3)
                    self.entries[x,y]["allyfarbe"] = farbe
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False


    def __list(self, cols, doerfer):
        """Erstellt eine Tabelle der Doerfer
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        tabelle = ausgabe.Tabelle()
        for col in cols:
            if col == "koords":
                tabelle.addColumn("X")
                tabelle.addColumn("Y")
            elif col not in ["ritternr", "allicolor"]:
                tabelle.addColumn(translate(col))
        for dorf in doerfer:
            line = []
            dorf = ausgabe.escape_row(dorf)
            for i in range(0, len(dorf)):
                if cols[i] == "koords":
                    x = dorf[i][0:3]
                    y = dorf[i][4:7]
                    link = "/show/feld/%s.%s" % (x, y)
                    line.append(ausgabe.link(link, x))
                    line.append(ausgabe.link(link, y))
                elif cols[i] == "ritternr":
                    # nachfolgenden Ritternamen verlinken
                    url = "/show/reich/%s" % dorf[i]
                    if cols[i+1] == "allicolor":
                        if dorf[i] is None:
                            link = "(nicht existent)"
                        else:
                            link = ausgabe.link(url, dorf[i+2], dorf[i+1])
                    else:
                        link = ausgabe.link(url, dorf[i+1])
                    line.append(link)
                elif cols[i] == "mauer":
                    mauer_string = {'o': "ohne", 'k': "kleine", 'm': "mittlere",
                            'g': "gro&szlig;e", 'u': "un&uuml;berwindbar",
                            'n': "?"}
                    line.append(mauer_string[dorf[i]])
                elif cols[i] == "aktdatum":
                    string = ausgabe.date_delta_string(dorf[i])
                    if dorf[i]:
                        delta = date.today() - dorf[i]
                    else:
                        delta = timedelta(weeks=9999)
                    if delta > timedelta(weeks=104):
                        line.append('<div style="color:red">%s</div>' % string)
                    elif delta > timedelta(weeks=52):
                        line.append('<div style="color:orange">%s</div>'
                                % string)
                    else:
                        line.append(string)
                elif cols[i-1] not in ["ritternr", "allicolor"]:
                    line.append(dorf[i])
            tabelle.addLine(line)
        return tabelle

    def list_by_feld(self, x, y):
        """Holt das Dorf auf einem Feld
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["dorf.ritternr", "allicolor", "rittername", "dorfname"]
        cols += ["aktdatum", "dorflevel", "mauer"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM dorf"
        sql += " JOIN ritter ON dorf.ritternr = ritter.ritternr"
        sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE koords = %s"
        try:
            self.cursor.execute(sql, x + ',' + y)
            armeen = self.cursor.fetchall()
            cols[0] = "ritternr" # war dorf.ritternr
            cols[5] = "level" # war dorflevel
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_by_reich(self, r_id):
        """Holt alle Doerfer eines Reiches mit r_id
        
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["koords", "dorfname", "aktdatum", "dorflevel", "mauer"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM dorf"
        sql += " JOIN ritter ON dorf.ritternr = ritter.ritternr"
        sql += " WHERE dorf.ritternr = %s"
        sql += " ORDER BY koords"
        try:
            self.cursor.execute(sql, r_id)
            armeen = self.cursor.fetchall()
            cols[3] = "level" # war dorflevel
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None

    def list_all(self):
        """Gibt eine Tabelle aller Doerfer
        
        @return: L{Tabelle<ausgabe.Tabelle>}
        """
        return self.list_by_allianz(-1)

    def list_by_allianz(self, a_id):
        """Holt alle Doerfer eines Allianz mit a_id

        @param a_id: Id der Allianz
        @type a_id: C{IntType}
        @rtype: L{Tabelle<ausgabe.Tabelle>}
        """

        cols = ["koords", "dorf.ritternr"]
        if a_id == -1:
            cols.append("allicolor")
        cols += ["rittername", "dorfname", "aktdatum", "dorflevel", "mauer"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM dorf"
        sql += " JOIN ritter ON dorf.ritternr = ritter.ritternr"
        sql += " LEFT JOIN allis ON ritter.alli = allis.allinr"
        if a_id != -1:
            sql += " WHERE allinr = %s"
        else:
            sql += " WHERE dorf.ritternr <> 0"
        sql += " ORDER BY aktdatum DESC, allicolor, rittername, koords"
        try:
            if a_id != -1:
                self.cursor.execute(sql, a_id)
            else:
                self.cursor.execute(sql)
            armeen = self.cursor.fetchall()
            cols[1] = "ritternr" # war dorf.ritternr
            if a_id == -1:
                cols[6] = "level" # war dorflevel
            else:
                cols[5] = "level" # war dorflevel
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return None


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
        ret =  (self.__is(STR,entry, MAN, DBCOL, "dorfname", 80)
                and self.__is(INT,entry, OPT, NO_DB, "x", 3)
                and self.__is(INT,entry, OPT, NO_DB, "y", 3)
                and self.__is(INT,entry, OPT, DBCOL, "dorflevel", 2)
                and self.__is(STR,entry, OPT, NO_DB, "besitzer",80)
                and self.__is(INT,entry, OPT, DBCOL, "ritternr",11)
                and self.__is(INT,entry, OPT, NO_DB, "detail",10)
                and self.__is(INT,entry, OPT, NO_DB, "last_seen",10)
                and self.__is(STR,entry, OPT, DBCOL, "mauer",1)
                and self.__is(STR,entry, OPT, DBCOL, "bemerkung",200)
                )
        self.__cols_gathered = True
        return ret

    def queue_entry(self, entry):
        """Nimmt das Dorf erstmal in eine TODO List auf.

        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind.
        @param entry: zu pruefender Eintrag
        @type entry: C{Dict}
        @rtype: C{BooleanType}
        """

        if self.__check_entry(entry):
            self.new_entries.append(entry)
            return True
        else:
            return False

    def exec_queue(self, sender_id):
        """Die TODO-Liste wird abgearbeitet.
        """

        self.__get_ritter_ids()
        empty_count = self.__empty(sender_id)
        update_count = self.__check_old(sender_id)
        insert_count = self.__insert()
        return empty_count, update_count, insert_count

    def __get_ritter_ids(self):
        """Holt IDs fuer alle Ritter von denen nur Namen bekannt sind
        """

        sqllist = []
        args = ()
        for entry in self.new_entries:
            if ("ritternr" not in entry and "besitzer" in entry
                    and entry["besitzer"] not in args):
                sqllist.append("rittername=%s")
                args += entry["besitzer"],
        if len(sqllist) > 0:
            sql = "SELECT ritternr, rittername FROM ritter WHERE "
            sql += " OR ".join(sqllist)
            self.try_execute_safe(sql, args)
            row = self.cursor.fetchone()
            while row != None:
                for entry in self.new_entries:
                    if "ritternr" not in entry and row[1] == entry["besitzer"]:
                        entry["ritternr"] = int(row[0])
                row = self.cursor.fetchone()
        # entferne entries die immernoch keine r_id haben
        i = 0
        while i < len(self.new_entries):
            if "ritternr" not in self.new_entries[i]:
                print "Ritter", self.new_entries[i]["besitzer"], "ist unbekannt!"
                # TODO: move that part to control or some other place
                #print get_ritter_id_form(self.new_entries[i]["ritter"]),"<br />"
                del self.new_entries[i]
            else:
                i += 1

    def __empty(self, sender_id):
        num_emptied = len(self.__empty_entries)
        if len(self.__empty_entries) > 0:
            sql = "REPLACE INTO dorf"
            sql += " (koords, dorfname, dorflevel, ritternr, aktdatum)"
            sql += " VALUES "
            sqllist = []
            args = ()
            for entry in self.__empty_entries:
                sqllist.append("(%s, 'leer', 0, 0, NOW())")
                args += str(entry["x"]) + "," + str(entry["y"]),
            sql += ", ".join(sqllist)
            self.try_execute_safe(sql, args)
        self.__empty_entries = []
        return num_emptied
        
    def __update(self, entry, sender_id):
        sql = "UPDATE dorf SET "
        sqllist = []
        args = ()

        for key in self.__entry_name_is_db_name:
            if key in entry:
                sqllist.append(key + "=%s")
                args += entry[key],
        if "last_seen" in entry:
            sqllist.append("aktdatum=FROM_UNIXTIME(%s)")
            args += entry["last_seen"],
        else:
            sqllist.append("aktdatum=NOW()")

        sql += ", ".join(sqllist)
        sql += " WHERE koords = %s"
        args += str(entry["x"]) + "," + str(entry["y"]),
        if "last_seen" in entry:
            sql += " AND aktdatum <= FROM_UNIXTIME(%s)"
            args += entry["last_seen"],
        return self.try_execute_safe_secondary(sql,args)

    def __check_old(self, sender_id):
        """Prueft ob an den Koordination schon Doerfer sind.

        Falls ja, wird das Dorf sofort aktualisiert
        und aus der TODO ausgetragen.
        @param sender_id: Sendendes Reich
        @rtype: C{IntType}
        """

        new = self.new_entries
        num_updated = 0
        if len(new) > 0:
            sql = "SELECT koords FROM dorf WHERE "
            sqllist = []
            args = ()
            for entry in new:
                sqllist.append("koords=%s")
                args += str(entry["x"]) + "," + str(entry["y"]),
            sql += " OR ".join(sqllist)
            self.try_execute_safe(sql, args)
            row = self.cursor.fetchone()
            while row != None:
                i = 0
                while i < len(new):
                    if (str(new[i]["x"]) + "," + str(new[i]["y"]) == row[0]):
                        if self.__update(new[i], sender_id):
                            num_updated += 1
                        del new[i]
                    else:
                        i += 1
                row = self.cursor.fetchone()
        return num_updated

    def __insert(self):
        num_inserted = 0
        for entry in self.new_entries:
            sql = "INSERT INTO dorf ("
            sqlcols = ["koords"]
            args = (str(entry["x"]) + "," + str(entry["y"]),)
            for key in self.__entry_name_is_db_name:
                if key in entry:
                    sqlcols.append(key)
                    args += entry[key],
            sqlcols.append("aktdatum")
            sql += ", ".join(sqlcols) + ") VALUES ("
            sql += ", ".join(["%s" for i in range(0,len(args))])
            if "last_seen" in entry:
                sql += ", FROM_UNIXTIME(%s)"
                args += entry["last_seen"],
            else:
                sql += ", NOW()"
            sql += ")"
            num_inserted += self.try_execute_safe(sql, args)
        self.new_entries = []
        return num_inserted

    def process_xml(self, node, sender_id):
        """Liest Daten aus einem XML-Dockument ein"""

        sicht = util.get_view_type(node)
        felder = node.xpathEval('feld')
        for feld in felder:
            entry = dict()
            entry["x"] = feld.prop("x");  entry["y"] = feld.prop("y")
            doerfer = feld.xpathEval('dorf')
            if len(doerfer) > 0:
                dorf = doerfer[0]
                entry["dorflevel"] = dorf.prop("level")
                entry["dorfname"] = dorf.prop("name")
                entry["besitzer"] = dorf.prop("besitzer")
                entry["detail"] = dorf.prop("detail")
                try:
                    detail = int(dorf.prop("detail"))
                    if detail & 16 == 16:
                        entry["mauer"] = 'u'
                    elif detail & 8 == 8:
                        entry["mauer"] = 'g'
                    elif detail & 4 == 4:
                        entry["mauer"] = 'm'
                    elif detail & 2 == 2:
                        entry["mauer"] = 'k'
                    elif detail & 1 == 1:
                        entry["mauer"] = 'o'
                    else:
                        entry["mauer"] = 'n'
                except ValueError:
                    print dorf.prop("detail"), "ung&uuml;ltig als Detail <br />"
                entry["bemerkung"] = dorf.prop("detail")
                # 256 sichtturm
                # 512 weitsichtturm
                # 1024 Kriegsakademie
                # 2048 Taverne
                if dorf.hasProp("last_seen"):
                    entry["last_seen"] = dorf.prop("last_seen")
                # TODO; aber eigenes Feld geht immer!
                # --> update auge to only send that one?
                if sicht == "turm" or "last_seen" in entry:
                    if not self.queue_entry(entry):
                        print entry, "<br />"
                        print "enthielt Fehler <br />"
            elif sicht == "turm":
                self.__empty_entries.append(entry)
            # TODO: eigenes Feld leeren wenn ohne Dorf (armeesicht)
        emptied, updated, added = self.exec_queue(sender_id)
        if (emptied + updated + added) > 0:
            print "Es wurden", emptied, "D&ouml;rfer geleert,"
            print updated, "aktualisiert und",
            print added, "neu hinzugef&uuml;gt.", "<br />"
        else:
            print "Keine D&ouml;rfer ge&auml;ndert.", "<br />"


# vim:set shiftwidth=4 expandtab smarttab:
