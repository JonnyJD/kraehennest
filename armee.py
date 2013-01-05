#!/usr/bin/env python
"""Armeedaten einlesen und ausgeben"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import ausgabe
from user import User
from model.armee import Armee


# Aufruf als Skript
#if __name__ == '__main__':
if True:
    form = cgi.FieldStorage()

    if "list" in form:
        ausgabe.print_header("Armeeliste")

        armee = Armee()
        armeetabelle = armee.list_all()
        print "Anzahl Armeen:", armeetabelle.length()
        armeetabelle.show()
    elif "action" in form:
        try:
            if "confirmation" in form and form["confirmation"].value=="yes":
                confirmation = True
            else:
                confirmation = False

            # das nur bei Armeen, aber mehr gibt es auch vorerst nicht
            h_id = form["id"].value
            armee = Armee(h_id)
            user = User()
            if ((config.is_kraehe() or user.r_id == armee.owner)
			    and form["action"].value == "deactivate"):
                # Hier ist keine Konfirmation noetig
                armee.deactivate()
                ausgabe.redirect("/show/reich/" + str(armee.owner), 303)
            elif config.is_admin() and form["action"].value == "free":
                ausgabe.print_header("Armee " + h_id + " freigeben")
                armee.show()
                url = "/free/armee/" + str(h_id)
                if confirmation and ausgabe.test_referer(url):
                    armee.free()
                else:
                    message = "Wollen sie diese Armee wirklich freigeben?"
                    url += "/yes"
                    ausgabe.confirmation(message, url)
            elif config.is_admin() and form["action"].value == "delete":
                url = "/delete/armee/" + str(h_id)
                if confirmation and ausgabe.test_referer(url):
                    armee.delete()
                    if armee.owner != None:
                        ausgabe.redirect("/show/reich/" + str(armee.owner), 303)
                    else:
                        ausgabe.redirect("/delete", 303)
                else:
                    ausgabe.print_header("Armee " + h_id + " l&ouml;schen")
                    armee.show()
                    message = "Wollen sie diese Armee wirklich l&ouml;schen?"
                    url += "/yes"
                    ausgabe.confirmation(message, url)
            else:
                action = form["action"].value
                message = "Werde " + action + " nicht ausf&uuml;hren!"
                ausgabe.print_header(message)
        except KeyError, e:
            ausgabe.print_header("Unbekannte Armee: " + e.args[0])
    else:
        print "leer"

    ausgabe.print_footer()


# vim:set shiftwidth=4 expandtab smarttab:
