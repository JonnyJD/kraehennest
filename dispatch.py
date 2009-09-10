#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
import re
from terrain import Terrain

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
    print "Content-type: text/html\n"

    if form.has_key("data"):
        data = form["data"].value
        sections = get_sections(data)

        if "felder" in sections:
            terrain = Terrain()
            terrain.process(sections["felder"])
        if "armeen" in sections:
            print "Armeen werden noch nicht gespeichert", "<br />"
    else:
        print "Es wurden keine Daten gesendet."


# vim:set shiftwidth=4 expandtab smarttab:
