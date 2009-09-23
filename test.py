"""Funktionen zum Testen der Implementation"""

import libxml2
import profile
import pstats
import dispatch

if __name__ == "__main__":
    dtd = libxml2.parseDTD(None, 'data.dtd')
    ctxt = libxml2.newValidCtxt()
    doc = libxml2.parseDoc(open('test.xml', 'r').read())
    if doc.validateDtd(ctxt, dtd):
        profile.run('dispatch.process(doc)', 'profile')
        pstats.Stats('profile').sort_stats('cum').print_stats('nest', 10)
    else:
        print "\nDokument ist fehlerhaft"


# vim:set shiftwidth=4 expandtab smarttab:
