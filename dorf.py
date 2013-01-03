#!/usr/bin/env python
"""Modul zum einlesen und ausgeben von Dorfdaten"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import ausgabe
from model import Dorf


# Aufruf als Skript
#if __name__ == '__main__':
if True:
    form = cgi.FieldStorage()

    if "list" in form:
        ausgabe.print_header("Dorfliste")

        dorf = Dorf()
        dorftabelle = dorf.list_all()
        print "Anzahl D&ouml;rfer:", dorftabelle.length()
        dorftabelle.show()
    else:
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
