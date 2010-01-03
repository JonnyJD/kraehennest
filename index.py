#!/usr/bin/python

#import cgitb
#cgitb.enable()

import config
import karte
import ausgabe

ausgabe.print_header("Kr&auml;hennest")

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

ausgabe.print_footer()

# vim:set shiftwidth=4 expandtab smarttab:
