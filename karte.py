#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
from terrain import Terrain

print 'Content-type: text/html\n'

form = cgi.FieldStorage()
if form.has_key("level"):
    level = form["level"].value
else:
    level = 'N'

terrain = Terrain()
terrain.fetch_data(level, 273)
width = 32 * (terrain.xmax - terrain.xmin + 1)
print '<table width="' + str(width) + '" cellspacing="0">'
for y in range(terrain.ymin, terrain.ymax + 1):
    print '<tr style="height:32px;">'
    for x in range(terrain.xmin, terrain.xmax + 1):
        if terrain.has(x,y):
            row = '<td background="/img/terrain/'
            row += terrain.get(x,y) + '.gif" '
            row += 'style="width:32px;"></td>'
            print row
        else:
            print '<td></td>'
    print '</tr>'
print '</table>'

# vim:set shiftwidth=4 expandtab smarttab:
