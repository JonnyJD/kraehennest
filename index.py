#!/usr/bin/python
"""Das ist die Indexseite mit Links zu Uebersichten."""

#import cgitb
#cgitb.enable()

from datetime import datetime, timedelta
import cgi
import config
from user import User
import karte
import ausgabe


# Aufruf als Skript
if __name__ == "__main__":
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
    if config.is_admin():
        print '<div class="box">'
        print '<h2>Administration</h2>'
        if config.is_kraehe():
            print '<a href="/karte/datenpflege.php">Datenpflege</a>'
            print ausgabe.link("/show/versionen", "Versionsliste", br=True)
            print ausgabe.link("/delete", "L&ouml;schliste", br=True)
        else:
            print ausgabe.link("/show/versionen", "Versionsliste")
        print '<br /><a href="/create_md5.html">Account erstellen</a>'
        print '</div>'
    karte.list_maps()

    ausgabe.print_footer()

# vim:set shiftwidth=4 expandtab smarttab:
