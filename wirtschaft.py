#!/usr/bin/env python
"""Modul zum Einlesen und Ausgeben von Waren"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import ausgabe
from wirtschaft import ware, rezept

# Aufruf als Skript
if __name__ == '__main__':
    import cgi
    form = cgi.FieldStorage()

    if "list" in form:
        if form["list"].value == "preise":
            ausgabe.print_header("Preisliste")
            warentabelle = ware.list_all()
            print "Anzahl Waren:", warentabelle.length()
            warentabelle.show()
        elif form["list"].value == "rezepte":
            ausgabe.print_header("Rezeptliste")
            rezepttabelle = rezept.list_all()
            print "Anzahl Rezepte:", rezepttabelle.length()
            rezepttabelle.show()
        elif form["list"].value == "gueter":
            ausgabe.print_header("G&uuml;terrezepte")
            rezepttabelle = rezept.list_gueter()
            print "Anzahl G&uuml;terrezepte:", rezepttabelle.length()
            rezepttabelle.show()
        elif form["list"].value == "gegenstaende":
            ausgabe.print_header("Gegenstandsrezepte")
            rezepttabelle = rezept.list_gegenstaende()
            print "Anzahl Gegenstandsrezepte:", rezepttabelle.length()
            rezepttabelle.show()
        elif form["list"].value == "runen":
            ausgabe.print_header("Runenrezepte")
            rezepttabelle = rezept.list_runen()
            print "Anzahl Runenrezepte:", rezepttabelle.length()
            rezepttabelle.show()
    else:
        ausgabe.print_header("Wirtschaft")
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
