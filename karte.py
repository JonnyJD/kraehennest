#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
from terrain import Terrain
from dorf import Dorf

print 'Content-type: text/html\n'

form = cgi.FieldStorage()
if form.has_key("level"):
    level = form["level"].value
else:
    level = 'N'

terrain = Terrain()
if form.has_key("name"):
    # benannte Kartenausschnitte
    if form["name"]. value == "kraehen":
        terrain.fetch_data(level, 256, 289, 280, 304)
    elif form["name"].value == "osten":
        if not form.has_key("level") or form["level"] == 'N':
            terrain.fetch_data(level, 261, 292, 287, 322)
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

if not form.has_key("clean") and level == 'N':
    show_dorf = True
    dorf = Dorf()
    dorf.fetch_data()
else:
    show_dorf = False

size = 32 
fontsize = 9
if form.has_key("size"):
    if form["size"].value == "small":
        size = 16
        fontsize = 5

print '<style type="text/css">'
print 'td {'
print 'font-size: ' + str(fontsize) + 'pt;'
print 'height: ' + str(size) + 'px;'
print 'width: ' + str(size) + 'px;'
print 'text-align:center; }'
print '</style>'
width = size * (terrain.xmax - terrain.xmin + 1)
print '<table width="' + str(width) + '" cellspacing="0" cellpadding="0">'
# X - Achse
print '<tr style="height:' + str(size) + 'px;"><td></td>'
for x in range(terrain.xmin, terrain.xmax + 1):
    print '<td>' + str(x) + '</td>'
for y in range(terrain.ymin, terrain.ymax + 1):
    print '<tr style="height:' + str(size) + 'px;"><td>' + str(y)  + '</td>'
    for x in range(terrain.xmin, terrain.xmax + 1):
        if terrain.has(x,y):
            row = '<td background="/img/terrain/' + str(size) + '/'
            row += terrain.get(x,y) + '.gif"'
            if show_dorf and dorf.has(x,y):
                dorf.get(x,y)
                row += ' style="color:' + dorf.entry['allyfarbe'] + ';">'
                if dorf.entry['rittername'] != ".":
                    row += dorf.entry['rittername'][0:3]
                else:
                    row += "_"
            else:
                row += '>'
            row += '</td>'
            print row
        else:
            print '<td></td>'
    print '<td>' + str(y) + '</tr>'
# X - Achse
print '<tr style="height:' + str(size) + 'px;"><td></td>'
for x in range(terrain.xmin, terrain.xmax + 1):
    print '<td>' + str(x) + '</td>'
print '</table>'

# vim:set shiftwidth=4 expandtab smarttab:
