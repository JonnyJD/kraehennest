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
if form.has_key("name"):
    # benannte Kartenausschnitte
    if form["name"].value == "osten":
        if not form.has_key("level") or form["level"] == 'N':
            terrain.fetch_data(level, 273)
        else:
            terrain.fetch_data(level, 261)
    elif form["name"].value == "westen":
        terrain.fetch_data(level, 225, 261, 287, 307)
    elif form["name"].value == "sueden":
        terrain.fetch_data(level, 240, 250, 320, 341)
    elif form["name"].value == "axt":
        terrain.fetch_data(level, 240, 260, 296, 314)
    elif form["name"].value == "schuetzen":
        terrain.fetch_data(level, 238, 247, 303, 312)
    elif form["name"].value == "drache":
        terrain.fetch_data(level, 206, 217, 351, 360)
    elif form["name"].value == "neu":
        terrain.add_cond("typ is not NULL")
        terrain.fetch_data(level)
else:
    terrain.fetch_data(level)

width = 32 * (terrain.xmax - terrain.xmin + 1)
print '<table width="' + str(width) + '" cellspacing="0">'
# X - Achse
print '<tr style="height:32px;"><td></td>'
for x in range(terrain.xmin, terrain.xmax + 1):
    print '<td>' + str(x) + '</td>'
for y in range(terrain.ymin, terrain.ymax + 1):
    print '<tr style="height:32px;"><td>' + str(y)  + '</td>'
    for x in range(terrain.xmin, terrain.xmax + 1):
        if terrain.has(x,y):
            row = '<td background="/img/terrain/'
            row += terrain.get(x,y) + '.gif" '
            row += 'style="width:32px;"></td>'
            print row
        else:
            print '<td></td>'
    print '<td>' + str(y) + '</tr>'
# X - Achse
print '<tr style="height:32px;"><td></td>'
for x in range(terrain.xmin, terrain.xmax + 1):
    print '<td>' + str(x) + '</td>'
print '</table>'

# vim:set shiftwidth=4 expandtab smarttab:
