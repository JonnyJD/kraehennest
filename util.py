"""Einige kleine Hilfsfunktionen"""

def print_error(e):
    print "Fehler %d: %s" % (e.args[0], e.args[1])

def print_html_error(e):
    print_error(e)
    print "<br />"

# vim:set shiftwidth=4 expandtab smarttab:
