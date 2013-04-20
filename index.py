#!/usr/bin/env python
"""Das ist die Indexseite mit Links zu Uebersichten."""

import config

if config.debug:
    import cgitb
    cgitb.enable()

from datetime import datetime, timedelta
import cgi
from user import User
import ausgabe
from view.karte import list_maps


# Aufruf als Skript
# mod_python.cgihandler doesn't count as direct
#if __name__ == "__main__":
if True:
    try:
        user = User()
        if user.last_seen_auge:
            delta = datetime.now() - user.last_seen_auge
        else:
            delta = timedelta(weeks=9999)

        styles = "#augenzeit {"
        styles += "    font-weight:bold;"
        if delta > timedelta(hours=48):
            styles += "    color:red;"
        styles += "}"
        ausgabe.print_header("Kr&auml;hennest",styles)

        augenstring = ausgabe.datetime_delta_string(user.last_seen_auge)
        print '<p>Der eingeloggte Benutzer <strong>' + user.name + '</strong>',
        print 'hat zuletzt <span id="augenzeit">' + augenstring + '</span>',
        print 'das Kr&auml;henauge benutzt.</p>'
    except KeyError, e:
        user = None
        ausgabe.print_header("Kr&auml;hennest")


    # Uebersichtsseiten
    if config.is_kraehe():
        print '<div class="box">'
        print '<h2>&Uuml;bersichtsseiten</h2>'
        print ausgabe.link("/show/allianzen", "Allianzen")
        print ausgabe.link("/show/reiche", "Reiche", br=True)
        print ausgabe.link("/show/doerfer", "D&ouml;rfer", br=True)
        print ausgabe.link("/show/armeen", "Armeen", br=True)
        print '</div>'
    # Direktlinks
    if config.is_kraehe():
        print '<div class="box">'
        print '<h2>Direktlinks</h2>'
        print ausgabe.link("/show/allianz/60", "Kr&auml;hen")
        if user and user.r_id:
            url = "/show/reich/" + str(user.r_id)
            rittername = cgi.escape(user.rittername)
            print ausgabe.link(url, rittername, br=True)
        print ausgabe.link("/show/reich/174", "Keiner", br=True)
        print ausgabe.link("/show/reich/113", "Plunkett", br=True)
        print '</div>'
    # Adminbereich
    print '<div class="box">'
    print '<h2>Administration</h2>'
    if config.is_admin():
        if config.is_kraehe():
            print '<a href="/karte/datenpflege.php">Datenpflege</a>'
            print ausgabe.link("/show/versionen", "Versionsliste", br=True)
            print ausgabe.link("/delete", "L&ouml;schliste", br=True)
        else:
            print ausgabe.link("/show/versionen", "Versionsliste")
    print '<br /><a href="/create_md5.html">Account erstellen</a>'
    if ausgabe.prefix:
        if ausgabe.prefix == "/ext":
            suffix = "extern"
	else:
            suffix = ausgabe.prefix[1:]
	auge = "/kraehenauge_" + suffix + ".user.js"
    	print ausgabe.link(auge, "Kr&auml;henauge", br=True)
    else:
        auge = "/auge/kraehenauge.user.js"
    	print ausgabe.link(auge, "Kr&auml;henauge", br=True)
    print '</div>'

    list_maps()

    ausgabe.print_footer()

# vim:set shiftwidth=4 expandtab smarttab:
