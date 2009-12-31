#!/usr/bin/python

#import cgitb
#cgitb.enable()

import config
import cgi
import os
from terrain import Terrain
from dorf import Dorf
from armee import Armee

print 'Content-type: text/html; charset=utf-8\n'
print '<html><head>'
print '<title>Kr&auml;henkarte</title>'
print '<link rel="stylesheet" type="text/css" href="stylesheet">'
print '</head>'
print '<body>'

if "REMOTE_USER" in os.environ:
    username = os.environ["REMOTE_USER"]
else:
    username = ""
is_kraehe = config.is_kraehe(username)

form = cgi.FieldStorage()

if "list" in form:
    if form["list"].value == "ksk":
        prefix = ""
    else:
        prefix = "/" + form["list"].value

    def print_link(link, name):
        url = prefix + "/show/karte" + link
        print '<a href="' + url + '">' + name + '</a><br />'
    def print_area_link(area, levels, name):
        if area != "":
            area = "/" + area
        print_link(area, name);
        for level in levels:
            link = area + "/u" + str(level)
            new_name = name + " Level U" + str(level)
            print_link(link, new_name)
        print "<br />"

    print '<style type="text/css">'
    print 'table {'
    print '     width: 100%;'
    print '     height: 100%;'
    print '}'
    print 'td { width: 34%; }'
    print '</style>'
    print '<table><tr>'
    if form["list"].value == "ksk":
        print '<th colspan=3>alte PHP-Karte</th>'
        print '</tr><tr style="height:50%;"><td>'
        print_link("",                "komplette Karte")
        print "</td><td>"
        print '<a href="/karte">Kraehengebiet (navigierbar)</a><br />'
        print "</td><td>"
        print_link("/neu", "aktuelle Doerfer (6 Monate)")
        print "</td></tr><tr>"
        print '<th colspan=3>neue Python-Karten</th>'
        print "</tr><tr><td>"
    else:
        print "<td>"
    if form["list"].value == "ksk":
        print_area_link("kraehen", [],     "Kraehengebiet")
        print "<br />"
    print_area_link("", [1,2,3,4],      "komplett (Normalgroesse)")
    print_link("/clean",                "komplett (ohne Doerfer)")
    print_link("/small",                "komplett (kleine Felder)")
    print_link("/clean/small",          "komplett (klein ohne Doerfer)")
    print_link("/verysmall",            "komplett (sehr kleine Felder)")
    print_link("/tiny",                 "komplett (winzige Felder)")
    print "<br />"
    print_link("/neu", "aktuelle Doerfer (6 Monate)")
    print "</td><td>"
    print_area_link("osten", [1,2,3,4], "Der Osten")
    print_area_link("westen", [1,2,3],  "Der Westen")
    print_area_link("sueden", [1,2,3],  "Der Sueden")
    print "</td><td>"
    print_area_link("drache", [1,2],    "Drachenhoehle")
    print_area_link("axt", [1,2,3],     "Axtwaechterquest")
    print_area_link("schuetzen", [1],   "Meisterschuetzenquest")
    print "</td></tr></table>"

else:
    # Zeige eine Karte

    if "level" in form:
        level = form["level"].value
    else:
        level = 'N'

    if form["layer"].value in ["clean", "leer"]:
        show_dorf = False
    elif level != "N":
        show_dorf = False
    else:
        show_dorf = True
        dorf = Dorf()
        if form["layer"].value == "neu":
            dorf.set_add_cond("datediff(now(), aktdatum) < 180")
        dorf.fetch_data()

    if is_kraehe and form["layer"].value not in ["clean", "leer"]:
        show_armeen = True
        armee = Armee()
        armee.fetch_data()
    else:
        show_armeen = False

    terrain = Terrain()
    #if form["layer"].value == "neu":
    #    terrain.set_add_cond("typ is not NULL")
    if "x1" in form:
        terrain.fetch_data(level, form["x1"].value,form["x2"].value,
                form["y1"].value, form["y2"].value)
    else:
        terrain.fetch_data(level)


    size = 32 
    fontsize = 9
    if "size" in form:
        if form["size"].value == "small":
            size = 16
            fontsize = 5
        elif form["size"].value == "verysmall":
            size = 8
            fontsize = 0
        elif form["size"].value == "tiny":
            size = 5
            fontsize = 0

    print '<style type="text/css">'
    print 'td {'
    print '    font-size: ' + str(fontsize) + 'pt;'
    print '    height: ' + str(size) + 'px;'
    print '    width: ' + str(size) + 'px;'
    print '    text-align:center; }'
    print 'div.armeen {'
    #print '    margin-left: ' + str(fontsize-5) + 'px;'
    print '    text-align:left;'
    print '    max-height: ' + str(fontsize-5) + 'px;'
    print '}'
    print 'span {'
    print '    display: inline-block;'
    if fontsize > 8:
        print '    height: ' + str(fontsize-5) + 'px;'
        print '    width: ' + str(fontsize-5) + 'px;'
    else:
        print '    height: 0px;'
        print '    width: 0px;'
    print '}'
    print 'span.a60 { background-color:red; }'
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
                row += terrain.get(x,y) + '.gif">'
                #if show_armeen:
                    # freundliche Armeen
                if show_dorf and dorf.has(x,y):
                    dorf.get(x,y)
                    row += '<div style="color:'+ dorf.entry['allyfarbe'] +';">'
                    if dorf.entry['rittername'] != ".":
                        row += dorf.entry['rittername'][0:3]
                    else:
                        row += "_"
                    row += '</div>'
                elif show_armeen:
                    row += '<div>&nbsp;</div>'
                if show_armeen:
                    # feindliche Armeen (erstmal alle)
                    row += '<div class="armeen">'
                    row += '<span></span>' # dummy fuer Formatierung
                    if armee.has(x,y):
                        for entry in armee.get(x,y):
                            row += '<span style="background-color:'
                            row += entry + '"></span>'
                    row += '</div>'
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

print "</body></html>"

# vim:set shiftwidth=4 expandtab smarttab:
