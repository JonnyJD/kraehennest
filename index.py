#!/usr/bin/python
"""Das ist die Indexseite mit Links zu Uebersichten."""

#import cgitb
#cgitb.enable()

import config
import karte
import ausgabe


# Aufruf als Skript
if __name__ == "__main__":
    ausgabe.print_header("Kr&auml;hennest")

    print '<p>eingeloggter Benutzer: ' + config.get_username() + '</p>'

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
        print '</div>'
    karte.list_maps()

    ausgabe.print_footer()

# vim:set shiftwidth=4 expandtab smarttab:
