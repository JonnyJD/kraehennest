#!/usr/bin/python

import cgitb
cgitb.enable()

import cgi
import re
import util
from xml.dom import minidom
from terrain import Terrain
#from armee import Armee

def get_sections(data):
    lines = data.splitlines();
    sections = dict()
    pos = 0;
    while pos < len(lines):
        result = re.match("^<([a-z]*)>", lines[pos])
        if result:
            section = result.group(1)
            start = pos
            while pos < len(lines) and not lines[pos] == "</"+section+">":
                pos += 1
            sections[section] = "\n".join(lines[start+1:pos])
        pos += 1
    if len(sections) == 0:
        sections["felder"] = "\n".join(lines)
    return sections


if __name__ == '__main__':
    form = cgi.FieldStorage()
    data = None
    print "Content-type: text/html\n"

    try:
        data = minidom.parseString(form.value).documentElement
    except Exception:
        print "Es wurden keine gueltigen Daten gesendet. <br />"

    if data != None:
        nodes = data.getElementsByTagName("auge")
        if (nodes.length > 0):
            util.track_client(nodes[0])

        nodes = data.getElementsByTagName("armeen")
        if (nodes.length > 0):
            #armee = Armee()
            #armee.process_xml(nodes[0])
            print nodes[0].toxml()
        nodes = data.getElementsByTagName("felder")
        if (nodes.length > 0):
            terrain = Terrain()
            terrain.process_xml(nodes[0])


# vim:set shiftwidth=4 expandtab smarttab:
