#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import util
import libxml2
from terrain import Terrain
from armee import Armee

if __name__ == '__main__':
    form = cgi.FieldStorage()
    valid = False
    print "Content-type: text/html\n"

    try:
        dtd = libxml2.parseDTD(None, 'data.dtd')
        ctxt = libxml2.newValidCtxt()
        doc = libxml2.parseDoc(form.value)
        if doc.validateDtd(ctxt, dtd):
            valid = True
        else:
            print "Es wurden keine gueltigen Daten gesendet. <br />"
    except libxml2.parserError:
        print "Es wurden keine sinnvollen Daten gesendet. <br />"


    if valid:
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


# vim:set shiftwidth=4 expandtab smarttab:
