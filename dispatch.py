#!/usr/bin/env python
"""Reicht einkommende XML-Dokumente auf passende Module auf"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import os
import util
import libxml2
from model.terrain import Terrain
from model.armee import Armee
from model.dorf import Dorf
from control import reich

def process(doc):
    """Reicht bestimmte Knoten zu Modulen weiter
    
    @param doc: das auseinanderzunehmende Dokument
    """

    data = doc.xpathEval('/data')[0]

    nodes = data.xpathEval('auge')
    if len(nodes) > 0:
        r_id = util.track_client(nodes[0])
    else:
        r_id = None

    nodes = data.xpathEval('rb/armeen')
    if len(nodes) > 0:
        armee = Armee()
        armee.process_xml(nodes[0], r_id)

    nodes = data.xpathEval('rb/felder')
    if len(nodes) > 0:
        terrain = Terrain()
        terrain.process_xml(nodes[0])
        dorf = Dorf()
        dorf.process_xml(nodes[0], r_id)

    nodes = data.xpathEval('rb/reiche')
    if len(nodes) > 0:
        reich.process_xml(nodes[0])


#if __name__ == '__main__':
if True:
    # Cross-Origin-Resource Sharing
    # noetig fuer cross-site-xmlhttprequest des Auges (einige Browser)
    print "Access-Control-Allow-Origin: http://www.ritterburgwelt.de"
    # note that * is not allowed together with credentials
    print "Access-Control-Allow-Credentials: true"
    if 'REQUEST_METHOD' not in os.environ:
        print "\nKeine REQUEST_METHOD"
    elif os.environ['REQUEST_METHOD'] == "OPTIONS":
        # "preflight"
        print "Access-Control-Allow-Methods: POST"
        print "Access-Control-Allow-Headers: Content-type"
        print "Access-Control-Max-Age: 86400\n" # 24 Stunden
    elif os.environ['REQUEST_METHOD'] != "POST":
        print "Status: 405 Method Not Allowed"
        print "Allow: POST, OPTIONS"
        print "Content-type: text/plain\n"
        print "Dateneingabe:"
        print os.environ['REQUEST_METHOD'], "Methode nicht zugelassen."
    else:
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
        except TypeError, e:
            print '<div style="background-color:red;">'
            print "Es gab ein Problem, bitte wende dich an Jonerian. <br />"
            print "Sende ihm bitte auch die RB-Seite in HTML in der"
            print "das Problem auftrat:"
            print "<br />", e
            print "</div>"


# vim:set shiftwidth=4 expandtab smarttab:
