#!/usr/bin/python

#import cgitb
#cgitb.enable()

import config
import re
import os
import karte

print 'Content-type: text/html; charset=utf-8\n'
print '<html><head>'
print '<title>Kr&auml;hendatenbank</title>'
print '<link rel="stylesheet" type="text/css" href="stylesheet">'
print '</head>'
print '<body>'

prefix = re.match("(.*)/show", os.environ['SCRIPT_URL']).group(1)

print '<style type="text/css">'
print 'td.karten { width:34%; }'
print '</style>'

print '<h1>Kr&auml;hendatenbank</h1>'

print '<p>eingeloggter Benutzer: ' + config.get_username() + '</p>'

# Uebersichtsseiten
if config.is_kraehe():
    print '<div class="box">'
    print '<h2>&Uuml;bersichtsseiten</h2>'
    print '<a href="' + prefix + '/show/reiche">Reiche</a>'
    print '<br /><a href="' + prefix + '/show/armeen">Armeen</a>'
    print '</div>'
# Adminbereich
if config.is_admin():
    print '<div class="box">'
    print '<h2>Administration</h2>'
    print '<a href="/karte/datenpflege.php">Datenpflege</a>'
    print '</div>'
karte.list_maps(prefix)

print "</body></html>"

# vim:set shiftwidth=4 expandtab smarttab:
