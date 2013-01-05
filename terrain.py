#!/usr/bin/env python
"""Skript um Terraindaten einzulesen und auszugeben"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import util
from model.terrain import Terrain


# Aufruf als Skript: Landschaftsaktualisierung
#if __name__ == '__main__':
if True:
    form = cgi.FieldStorage()
    print "Content-type: text/plain\n"

    util.track_client_version(form)

    if form.has_key("data"):
        terrain = Terrain()
        terrain.process(form["data"].value)
    else:
        terrain = Terrain()
        terrain.process("")


# vim:set shiftwidth=4 expandtab smarttab:
