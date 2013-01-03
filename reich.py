#!/usr/bin/env python
"""Eine Skript um Reichsdaten ein- und auszulesen.

Aufgerufen als Skript kann es als Query-String ein XML-Dokument bekommen
und liest dann die Ritternummern in die Datenbank ein.

Bekommt es ein Feld C{list}, dann werden alle Reiche aufgelistet.

Bekommt es ein Feld C{id}, dann zeigt es die Details eines bestimmten Reiches.
"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import libxml2
from types import StringType

import ausgabe
from model.reich import Reich
from model.armee import Armee
from model.dorf import Dorf
from view import allianz
from view.reich import list, status_string


# Aufruf als Skript: Reich eintragen
#if __name__ == '__main__':
if True:
    form = cgi.FieldStorage()

    if type(form.value) == StringType:
        # Reichsdaten vom RB Server einlesen
        try:
            root = libxml2.parseDoc(form.value)
            process_response_xml(root)
        except libxml2.parserError:
            print "Es wurden keine gueltigen Daten gesendet. <br />"
    elif "list" in form:
        ausgabe.print_header("Reichsliste")

        reichtabelle = list()
        print "Es sind", reichtabelle.length(), "Reiche in der Datenbank"
        reichtabelle.show()

        ausgabe.print_footer()
    elif "id" in form:
        r_id = form["id"].value
        try:
            reich = Reich(r_id)
            rittername = cgi.escape(reich.rittername)
            ausgabe.print_header("Reich von: " + rittername)

            print '<table>'
            print '<tr><td>Name: </td>'
            print '<td colspan="4" style="font-weight:bold;">&nbsp;',
            print ausgabe.escape(reich.name) + '</td></tr>'
            print '<tr><td>Allianz: </td><td colspan="4">&nbsp;',
            allianzname = ausgabe.escape(reich.ally_name)
            print allianz.link(reich.ally, allianzname, reich.ally_color),
            print '</td></tr>'
            dorf = Dorf()
            dorftabelle = dorf.list_by_reich(r_id)
            print '<tr><td><a href="#doerfer">D&ouml;rfer:</a> </td>'
            print '<td>&nbsp;&nbsp;' + str(dorftabelle.length()) + '</td>'
            armee = Armee()
            armeetabelle = armee.list_by_reich(r_id)
            print '<td>&nbsp;&nbsp;</td>'
            print '<td><a href="#armeen">Armeen:</a> </td>'
            print '<td>&nbsp;&nbsp;' + str(armeetabelle.length()) + '</td>'
            print '</tr><tr>'
            print '<td>Reichslevel: </td>'
            print '<td>&nbsp;&nbsp;' + str(reich.level) + '</td>'
            print '<td>&nbsp;&nbsp;</td>'
            print '<td>Platzierung: </td>'
            print '<td>&nbsp;&nbsp;' + str(reich.top10) + '</td>'
            print '</tr><tr>'
            print '<td>Letzter Zug: </td>'
            print '<td colspan="3">&nbsp;&nbsp;'+ reich.last_turn + '</td>'
            if reich.status is not None:
                print '</tr><tr>'
                print '<td>Status: </td>'
                print '<td colspan="3">&nbsp;&nbsp;' + reich.status + '</td>'
            print '</tr>'
            print '</table>'

            print '<h2 id="doerfer">D&ouml;rfer</h2>'
            dorftabelle.show()
            print '<h2 id="armeen">Armeen</h2>'
            armeetabelle.show()
        except KeyError, e:
            ausgabe.print_header("Unbekanntes Reich: " + e.args[0])

        ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
