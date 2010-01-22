#!/usr/bin/python
"""Reicht einkommende XML-Dokumente auf passende Module auf"""

#import cgitb
#cgitb.enable()

import cgi
import util
import libxml2
from terrain import Terrain
from armee import Armee

def process(doc):
    """Reicht bestimmte Knoten zu Modulen weiter
    
    @param doc: das auseinanderzunehmende Dokument
    """

    data = doc.xpathEval('/data')[0]

    nodes = data.xpathEval('auge')
    if len(nodes) > 0:
        util.track_client(nodes[0])

    nodes = data.xpathEval('rb/armeen')
    if len(nodes) > 0:
        armee = Armee()
        armee.process_xml(nodes[0])

    nodes = data.xpathEval('rb/felder')
    if len(nodes) > 0:
        terrain = Terrain()
        terrain.process_xml(nodes[0])

if __name__ == '__main__':
    form = cgi.FieldStorage()
    valid = False
    print "Content-type: text/html\n"

    try:
        dtd = libxml2.parseDTD(None, 'data.dtd')
        ctxt = libxml2.newValidCtxt()
        doc = libxml2.parseDoc(form.value)
        if doc.validateDtd(ctxt, dtd):
            process(doc)
        else:
            print "Es wurden keine gueltigen Daten gesendet. <br />"
    except libxml2.parserError:
        print "Es wurden keine sinnvollen Daten gesendet. <br />"
    except TypeError:
        print '<div style="background-color:red;">'
        print "Es gab ein Problem, bitte wende dich an Jonerian. <br />"
        print "Sende ihm bitte auch die RB-Seite in HTML in der"
        print "das Problem auftrat.</div>"


# vim:set shiftwidth=4 expandtab smarttab:
