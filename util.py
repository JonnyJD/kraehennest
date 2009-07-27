"""Einige kleine Hilfsfunktionen"""

import sys

def print_error(e):
    print "Fehler %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

# vim:set shiftwidth=4 expandtab smarttab:
