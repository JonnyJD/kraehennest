#!/usr/bin/env python
"""Die Grundstruktur von Klassen die Daten zu einem bestimmten Feld bearbeiten.
"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import ausgabe
from model.feld import Feld
from armee import Armee
from dorf import Dorf
from view import karte


# Aufruf als Skript: Felddetails
#if __name__ == '__main__':
if True:

    form = cgi.FieldStorage()

    if "level" in form:
        level = form["level"].value
    else:
        level = "N"
    x = form["x"].value
    y = form["y"].value

    if level != "N":
        title = "Feld " + level + ": " + x + ", " + y
    else:
        title = "Feld " + x + ", " + y

    styles = karte.create_styles(32, 9)
    ausgabe.print_header(title, styles)

    print '<div class="right_map">'
    print karte.small_map(int(x), int(y), level)
    print '</div>'

    feld = Feld(int(x), int(y), level)
    print '<img src="/img/terrain/32/' + str(feld.terrain) + '.gif"';
    print 'style="vertical-align:middle; margin-left:20px;">'
    print '<span style="display:inline-block; width:100px;">'
    if feld.typ > 1:
        print ' Typ', 'I' * feld.typ
    print '</span>'
    print '<span style="margin-left:200px;">'
    print karte.center_link(int(x), int(y), level)
    print '</span>'

    if level == "N":
        print "<h2>Dorf</h2>"
        dorf = Dorf()
        dorftabelle = dorf.list_by_feld(x, y)
        if dorftabelle.length() > 1:
            print "Mehrere D&ouml;rfer?? <br /><br />"
        dorftabelle.show()

    print '<h2 style="clear:right">Armeen</h2>'
    armee = Armee()
    armeetabelle = armee.list_by_feld(level, x, y)
    if armeetabelle.length() > 0:
        print "Anzahl Armeen:", armeetabelle.length()
    armeetabelle.show()

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
