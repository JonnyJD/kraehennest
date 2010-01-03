#!/usr/bin/python

#import cgitb
#cgitb.enable()

import config
import karte
import ausgabe

title = "Kr&auml;hennest"
print 'Content-type: text/html; charset=utf-8\n'
print '<html><head>'
print '<title>' + title + '</title>'
print '<link rel="stylesheet" type="text/css" href="stylesheet">'
print '</head>'
print '<body>'

print '<style type="text/css">'
print 'td.karten { width:34%; }'
print '</style>'

print '<h1>' + title + '</h1>'

print '<p>eingeloggter Benutzer: ' + config.get_username() + '</p>'

# Uebersichtsseiten
if config.is_kraehe():
    print '<div class="box">'
    print '<h2>&Uuml;bersichtsseiten</h2>'
    print '<a href="' + ausgabe.prefix + '/show/allianzen">Allianzen</a>'
    print '<br /><a href="' + ausgabe.prefix + '/show/reiche">Reiche</a>'
    print '<br /><a href="' + ausgabe.prefix + '/show/doerfer">D&ouml;rfer</a>'
    print '<br /><a href="' + ausgabe.prefix + '/show/armeen">Armeen</a>'
    print '</div>'
# Adminbereich
if config.is_admin():
    print '<div class="box">'
    print '<h2>Administration</h2>'
    print '<a href="/karte/datenpflege.php">Datenpflege</a>'
    print '<br /><a href="' + ausgabe.prefix + '/show/versionen">'
    print 'Versionsliste</a>'
    print '</div>'
karte.list_maps()

print "</body></html>"

# vim:set shiftwidth=4 expandtab smarttab:
