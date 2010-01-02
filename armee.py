#!/usr/bin/python

#import cgitb
#cgitb.enable()

import rbdb
import util
import re
from feld import Feld
from reich import get_ritter_id_form
from ausgabe import Tabelle

MAN     = True;         OPT   = False
DBCOL   = True;         NO_DB = False
INT     = True;         STR   = False

class Armee(Feld):
    """Eine Klasse um Armeedaten ein- und auszulesen.
    
    Einlesen:
        Mit queue_entry(fields) werden die Felder einzeln uebergeben.
        Mit exec_queue() werden dann alle eingetragen, falls nicht vorhanden.

    Auslesen:
        Mit set_add_cond() kann man eine weitere Bedingung vorgeben.
        (dabei sollte man die sql strings absichern!)
        Danach wird mit fetch_data([level[, xmin[, xmax[, ymin[, ymax]]]]])
        alles passende von der Datenbank geladen.
        Mit has(x,y) und get(x,y) kann man dann einzeln zugreifen.
    
    Beenden:
        Mit disconnect() kann die Datenbankverbindung beendet werden.
        Danach koennen nurnoch die bereits geladenen Daten geholt werden."""

    def __init__(self):
        Feld.__init__(self)
        self.table_name = "armeen"
        self.__entry_name_is_db_name = []
        self.__cols_gathered = False
        self.__int_columns = []
        self.__inactive_entries = []

    def __is(self, is_int, entry, mandatory, db_col, key, length):
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
            print entry[key], "ist nicht zulaessig als", key, "<br />"
        return ret

    def __check_entry(self, entry):
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
        return (self.__is(INT, entry, MAN, NO_DB, "x", 3)
                and self.__is(INT,entry, MAN, NO_DB, "y", 3)
                and self.__is(STR,entry, MAN, NO_DB, "level", 2)
                )

    def queue_entry(self, entry):
        """Nimmt eine Armee zum Eintragen erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind."""

        if self.__check_entry(entry):
            self.new_entries.append(entry)
            return True
        else:
            return False


    def queue_inactive(self, entry):
        """Nimmt eine Armee zum Deaktivieren erstmal in einer TODO-Liste auf.
        
        Es wird zurueckgegeben ob die Daten syntaktisch korrekt sind."""

        if self.__check_inactive(entry):
            self.__inactive_entries.append(entry)
            return True
        else:
            return False

    def __deactivate(self):
        """Deaktiviert alle Armeen in der inactie Liste."""

        if len(self.__inactive_entries) > 0:
            sql = "UPDATE armeen SET active=0 WHERE "
            sqllist = []
            args = ()
            for entry in self.__inactive_entries:
                sqllist.append("(level=%s AND x=%s AND y=%s)")
                args += entry["level"], entry["x"], entry["y"]
            
            sql += "(" + " OR ".join(sqllist) + ") AND "
            # die hier anwesenden Armeen garnicht erst deaktivieren
            sqllist = []
            for entry in self.new_entries:
                sqllist.append("h_id<>%s")
                args += entry["h_id"],
            sql += " AND ".join(sqllist)
            self.__inactive_entries = []
            return self.try_execute_safe(sql, args)
        else:
            return 0

    def __get_ritter_ids(self):
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
            sqllist.append("status='S'")
        else:
            sqllist.append("active=1")
            sqllist.append("status=NULL")
        sql += ", ".join(sqllist)
        sql += " WHERE h_id = %s"
        args += entry["h_id"],
        return self.try_execute_safe_secondary(sql, args)


    def __check_old(self):
        """Gleicht die einzufuegenden Armeen mit in der DB vorhandenen ab.
        
        Identische Eintragungen werden aus der TODO-Liste entnommen
        und Aenderungen werden sofort ausgefuehrt."""

        new = self.new_entries
        num_updated = 0
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
                    else:
                        print "Konnte", new[i]["name"], "nicht aktualisieren"
                    del new[i]
                else:
                    i += 1
            row = self.cursor.fetchone()
        return num_updated


    def __insert(self):
        """Fuegt alle in der TODO-Liste verbliebenen Eintraege in die DB ein.

        Es wird hier davon ausgegangen, dass diese Eintraege
        noch nicht in der Datenbank vorhanden sind."""

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
                args += "S",
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
        Die Anzahl der aktualisierten und der neuen Eintraege
        wird zurueckgegeben."""

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
            print "FEHLER: Level '" + level + "' ist ungueltig"

    def __get_entries(self):
        """Holt alle Eintraege im Bereich von der Datenbank."""

        sql = "SELECT x, y, ritternr, allicolor, name, size, strength"
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
                entry["name"] = row[4]
                entry["size"] = row[5]
                entry["strength"] = row[6]
                if (row[0],row[1]) not in self.entries:
                    self.entries[row[0],row[1]] = []
                self.entries[row[0],row[1]].append(entry)
                row = self.cursor.fetchone()
            return True
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def __list(self, cols, armeen):
        tabelle = Tabelle()
        for col in cols:
            if col != "ritternr":
                tabelle.addColumn(col)
        for armee in armeen:
            line = []
            for i in range(0, len(armee)):
                if cols[i] == "ritternr":
                    # nachfolgenden Ritternamen verlinken
                    col = '<a href="reich/' + str(armee[i]) + '"'
                    if armee[i] == 174: # Keiner
                        col += ' style="color:green"'
                    if armee[i] == 113: # Plunkett
                        col += ' style="color:red"'
                    col += '>' + armee[i+1] + '</a>'
                    line.append(col)
                elif cols[i-1] != "ritternr":
                    line.append(armee[i])
            tabelle.addLine(line)
        return tabelle

    def list_by_reich(self, r_id):
        """Holt alle Armeen eines Reiches mit r_id"""

        cols = ["level", "x", "y", "name", "last_seen"]
        cols += ["size", "strength", "bp", "ap", "schiffstyp"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " WHERE r_id = %s"
        sql += " AND active = 1"
        sql += " AND last_seen >= DATE_SUB(now(), interval 30 hour)"
        sql += " ORDER BY last_seen DESC"
        try:
            self.cursor.execute(sql, r_id)
            armeen = self.cursor.fetchall()
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def list_all(self):
        return self.list_by_allianz(-1)

    def list_by_allianz(self, a_id):
        """Holt alle Armeen eines Allianz mit a_id"""

        cols = ["level", "x", "y", "ritternr", "rittername", "name"]
        cols += ["last_seen"]
        cols += ["size", "strength", "bp", "ap", "schiffstyp"]
        sql = "SELECT " + ", ".join(cols)
        sql += " FROM armeen"
        sql += " JOIN ritter ON armeen.r_id = ritternr"
        sql += " JOIN allis ON ritter.alli = allis.allinr"
        sql += " WHERE"
        sql += " active = 1"
        if a_id != -1:
            sql += " AND allinr = %s"
        sql += " AND last_seen >= DATE_SUB(now(), interval 30 hour)"
        sql += " ORDER BY last_seen DESC"
        try:
            if a_id != -1:
                self.cursor.execute(sql, a_id)
            else:
                self.cursor.execute(sql)
            armeen = self.cursor.fetchall()
            return self.__list(cols, armeen)
        except rbdb.Error, e:
            util.print_html_error(e)
            return False

    def process_xml(self, node):

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
        if len(armeen) > 0:
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
                    entry["schiffstyp"] = schiffe[0].prop("typ")
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
            inactive, updated, added = self.exec_queue()
            if (inactive + updated + added) > 0:
                print "Es wurden", inactive, "Armeen deaktiviert,",
                print updated, "aktualisiert und",
                print added, "neu hinzugefuegt.", "<br />"
            else:
                print "Keine Armeen gespeichert.", "<br />"
        else:
            print 'Es wurden keine Armeedaten gesendet.', "<br />"

if __name__ == '__main__':
    print 'Content-type: text/html; charset=utf-8\n'
    print '<html><head>'
    print '<link rel="stylesheet" type="text/css" href="../stylesheet">'
    import cgi


    form = cgi.FieldStorage()
    root = None

    if "list" in form:
        from armee import Armee

        print '<title>Armeeliste</title>'
        print '</head>'
        print '<body>'

        armee = Armee()
        armeetabelle = armee.list_all()
        print "Anzahl Armeen:", armeetabelle.length()
        armeetabelle.show()
    else:
        print "leer"

    print'</body></html>'


# vim:set shiftwidth=4 expandtab smarttab:
