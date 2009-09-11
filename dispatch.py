#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import util
import libxml2
from terrain import Terrain
#from armee import Armee

if __name__ == '__main__':
    form = cgi.FieldStorage()
    data = None
    print "Content-type: text/html\n"

    try:
        data = libxml2.parseDoc(form.value).xpathEval('/data')[0]
    except libxml2.parserError:
        print "Es wurden keine gueltigen Daten gesendet. <br />"

    if data != None:

        nodes = data.xpathEval('auge')
        if len(nodes) > 0:
            util.track_client(nodes[0])

        nodes = data.xpathEval('rb/armeen')
        if len(nodes) > 0:
        #    armee = Armee()
        #    armee.process_xml(nodes[0])
            print nodes[0].getContent(), "<br />"

        nodes = data.xpathEval('rb/felder')
        if len(nodes) > 0:
            terrain = Terrain()
            terrain.process_xml(nodes[0])


# vim:set shiftwidth=4 expandtab smarttab:
