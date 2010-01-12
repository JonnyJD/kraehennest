#!/usr/bin/python
"""Das ist die Indexseite mit Links zu Uebersichten."""

#import cgitb
#cgitb.enable()

from datetime import datetime, timedelta
import config
import user
import karte
import ausgabe


# Aufruf als Skript
if __name__ == "__main__":
    username = config.get_username()
    augenzeit = user.last_seen_auge()
    if augenzeit:
        delta = datetime.now() - augenzeit
    else:
        delta = timedelta(weeks=9999)

    styles = "#augenzeit {"
    styles += "    font-weight:bold;"
    if delta > timedelta(hours=48):
        styles += "    color:red;"
    styles += "}"
    ausgabe.print_header("Kr&auml;hennest",styles)

    augenstring = ausgabe.datetime_delta_string(augenzeit)
    print '<p>Der eingeloggte Benutzer <strong>' + username + '</strong>',
    print 'hat zuletzt <span id="augenzeit">' + augenstring + '</span>',
    print 'das Kr&auml;henauge benutzt.</p>'

    # Uebersichtsseiten
    if config.is_kraehe():
        print '<div class="box">'
        print '<h2>&Uuml;bersichtsseiten</h2>'
        print ausgabe.link("/show/allianzen", "Allianzen")
        print ausgabe.link("/show/reiche", "Reiche", br=True)
        print ausgabe.link("/show/doerfer", "D&ouml;rfer", br=True)
        print ausgabe.link("/show/armeen", "Armeen", br=True)
        print '</div>'
    # Adminbereich
    if config.is_admin():
        print '<div class="box">'
        print '<h2>Administration</h2>'
        print '<a href="/karte/datenpflege.php">Datenpflege</a>'
        print ausgabe.link("/show/versionen", "Versionsliste", br=True)
        print ausgabe.link("/delete", "L&ouml;schliste", br=True)
        print '</div>'
    karte.list_maps()

    ausgabe.print_footer()

# vim:set shiftwidth=4 expandtab smarttab:
