#!/usr/bin/python

#import cgitb
#cgitb.enable()

import config
import cgi
import os
import re
from terrain import Terrain
from dorf import Dorf
from armee import Armee


prefix = re.match("(.*)/show", os.environ['SCRIPT_URL']).group(1)

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

def list_maps(prefix):
    print '<style type="text/css">'
    print 'td.karten { width:34%; }'
    print '</style>'

    print '<div class="box" style="clear:both; width:100%;">'
    print '<h2>Karten</h2>'
    print '<table style="width:100%">'
    print '<tr><td class="karten">'
    if config.is_kraehe():
        text = '<span style="font-weight:bold;">Kraehengebiet</span>'
        print_area_link("kraehen", [], text)
    elif config.is_tw():
        text = '<span style="font-weight:bold;">Der Osten</span>'
        print_area_link("osten", [], text)
    print '<br />'
    print_area_link("", [1,2,3,4],      "komplett (Normalgroesse)")
    print_link("/clean",                "komplett (ohne Doerfer)")
    print_link("/small",                "komplett (kleine Felder)")
    print_link("/clean/small",          "komplett (klein ohne Doerfer)")
    print_link("/verysmall",            "komplett (sehr kleine Felder)")
    print_link("/tiny",                 "komplett (winzige Felder)")
    print '<br />'
    print_link("/neu", "aktuelle Doerfer (6 Monate)")
    print '</td><td class="karten">'
    if config.is_tw():
        text = '<span style="font-weight:bold;">Der Osten</span>'
    else:
        text = "Der Osten"
    print_area_link("osten", [1,2,3,4], "Der Osten")
    print_area_link("westen", [1,2,3],  "Der Westen")
    print_area_link("sueden", [1,2,3],  "Der Sueden")
    print '</td><td class="karten">'
    print_area_link("drache", [1,2],    "Drachenhoehle")
    print_area_link("axt", [1,2,3],     "Axtwaechterquest")
    print_area_link("schuetzen", [1],   "Meisterschuetzenquest")
    print '</td></tr></table>'
    print '</div>'


# Aufruf direkt: Karten anzeigen
if __name__ == '__main__':
    form = cgi.FieldStorage()

    if "list" in form:
        title = "Kr&auml;henkarten"
    else:
        title = "Kr&auml;henkarte"
    print 'Content-type: text/html; charset=utf-8\n'
    print '<html><head>'
    print '<title>' + title + '</title>'
    print '<link rel="stylesheet" type="text/css" href="stylesheet">'
    if config.is_kraehe():
        print '<script src="javascript" type="text/javascript"></script>'
    print '</head>'
    print '<body>'

    if "list" in form:
        print '<h1>' + title + '</h1>'
        list_maps(prefix)
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

        if config.is_kraehe() and form["layer"].value not in ["clean", "leer"]:
            show_armeen = True
            armee = Armee()
            armee.fetch_data(level)
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
        if fontsize == 0:
            show_dorf = False
            show_armeen = False

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
        print '.navi {'
        if int(form["x2"].value) >= 999:
            print '    background-color:#333333;'
        print '    font-weight:bold;'
        print '    font-size:12pt;'
        print '}'
        print '</style>'

        width = size * (terrain.xmax - terrain.xmin + 1)

        if config.is_kraehe():
            # Dorfdetail
            print '<div id="dorfdetail" style="z-index:2; position:fixed;'
            print ' top:5px; left:38px; width:85em;'
            print ' font-size:9pt; background-color:#333333;'
            print ' padding:5px;"><div>&nbsp;</div></div>'
            # Armeedetail
            print '<div id="armeedetail" style="z-index:2; position:fixed;'
            print ' top:400px; right:5px; width:13em; height:25em;'
            print ' font-size:9pt; background-color:#333333;'
            print ' padding:5px;"><div>&nbsp;</div></div>'
            print '<br /><div></div>'


        def nav_link(direction, amount, text):
            x1 = int(form["x1"].value); x2 = int(form["x2"].value)
            y1 = int(form["y1"].value); y2 = int(form["y2"].value)
            if direction == "nord":
                y1 -= amount; y2 = y1 + 21;
            if direction == "sued":
                y2 += amount; y1 = y2 - 21;
            if direction == "ost":
                x1 -= amount; x2 = x1 + 33;
            if direction == "west":
                x2 += amount; x1 = x2 - 33;
            link = '<a href=' + prefix + '/show/karte/'
            link += str(x1) + '.' + str(y1) + '-' + str(x2) + '.' + str(y2)
            if level != 'N':
                link += '/' + level
            if "size" in form and form["size"].value != "normal":
                link += '/' + form["size"].value
            return link + '>' + text + '</a>'

        def level_link(direction):
            x1 = int(form["x1"].value); x2 = int(form["x2"].value)
            y1 = int(form["y1"].value); y2 = int(form["y2"].value)
            if ((direction == "hoch" and level != 'N')
                    or (direction == "runter" and level != 'u5')):
                link = '<a href=' + prefix + '/show/karte/'
                link += str(x1) + '.' + str(y1) + '-' + str(x2) + '.' + str(y2)
                if direction == "hoch":
                    if level != "u1":
                        new_level = 'u' + str(int(level[1])-1)
                        link += '/' + new_level
                    else:
                        new_level = 'N'
                if direction == "runter":
                    if level == "N":
                        new_level = 'u1'
                    else:
                        new_level = 'u' + str(int(level[1])+1)
                    link += '/' + new_level
                if "size" in form and form["size"].value != "normal":
                    link += '/' + form["size"].value
                return link + '>' + new_level + '</a>'
            else:
                return '&nbsp;'

        # Kartennavigation
        print '<table style="z-index:2; position:fixed; top:70px; right:5px;">'
        if int(form["x2"].value) < 999:
            # Richtungen
            print '<tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('nord', 17, '&uArr;')
            print '</td></tr><tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('nord', 3, '&uarr;')
            print '</td></tr><tr>'
            print '<td class="navi">' + nav_link('ost', 24, '&lArr;') + '</td>'
            print '<td class="navi">' + nav_link('ost', 4, '&larr;') + '</td>'
            print '<td>'
            if config.is_kraehe():
                print '<a href="' + prefix + '/show/karte/kraehen">&bull;</a>'
            elif config.is_tw():
                print '<a href="' + prefix + '/show/karte/osten">&bull;</a>'
            print '</td>'
            print '<td class="navi">' + nav_link('west', 4, '&rarr;') + '</td>'
            print '<td class="navi">' + nav_link('west', 24, '&rArr;') + '</td>'
            print '</tr><tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('sued', 3, '&darr;')
            print '</td></tr><tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('sued', 17, '&dArr;')
        else:
            print '<tr><td class="navi" colspan="3">'
            if config.is_kraehe():
                print '<a href="' + prefix + '/show/karte/kraehen">HOME</a>'
            elif config.is_tw():
                print '<a href="' + prefix + '/show/karte/osten">HOME</a>'
        print '</td></tr><tr><td>&nbsp;</td></tr>'
        # Level
        print '<tr><td></td><td></td><td class="navi">' + level_link("hoch")
        print '</td></tr>'
        print '<tr><td></td><td></td><td class="navi">' + level + '</td></tr>'
        print '<tr><td></td><td></td><td class="navi">' + level_link("runter")
        print '</td></tr>'
        print '</table>'

        # zurueck zum Datenbankindex
        if int(form["x2"].value) < 999:
            print '<div style="z-index:2; position:fixed;'
            print ' bottom:70px; right:70px;" class="navi">'
            if config.is_kraehe():
                print '<a href="' + prefix + '/show">Index</a></div>'
            else:
                print '<a href="' + prefix + '/show/karten">Index</a></div>'

        print '<table width="' + str(width),
        print '" cellspacing="0" cellpadding="0">'
        # X - Achse
        print '<tr style="height:' + str(size) + 'px;"><td></td>'
        for x in range(terrain.xmin, terrain.xmax + 1):
            print '<td>' + str(x) + '</td>'
        for y in range(terrain.ymin, terrain.ymax + 1):
            print '<tr style="height:' + str(size) + 'px;">'
            print '<td>' + str(y)  + '</td>'
            for x in range(terrain.xmin, terrain.xmax + 1):
                if terrain.has(x,y):
                    terrain.get(x,y)
                    row = '<td background="/img/terrain/' + str(size) + '/'
                    row += terrain.entry["terrain"] + '.gif"'
                    if config.is_kraehe():
                        row += ' onmouseover="showPos(\''
                        row += str(x) + "," + str(y)
                        if show_dorf and dorf.has(x,y):
                            dorf.get(x,y)
                            list = []
                            for col in ['rittername', 'alliname', 'dorfname',
                                    'dorflevel', 'mauer', 'aktdatum']:
                                list.append(str(dorf.entry[col]))
                            list = '|' + '|'.join(list)
                            if armee.has(x,y):
                                for entry in armee.get(x,y):
                                    list += '|' + entry["allyfarbe"]
                                    list += '|' + entry["name"]
                                    if entry["size"] == None:
                                        list += '|?'
                                    else:
                                        list += '|' + str(entry["size"])
                                    if entry["strength"] == None:
                                        list += '|?'
                                    else:
                                        list += '|' + str(entry["strength"])
                            list = list.replace("'", "\\'")
                            row += list.replace('"', "&quot;")
                        row += '\')" onmouseout="delPos()"'
                    row += '>'
                    if show_dorf and dorf.has(x,y):
                        dorf.get(x,y)
                        row += '<div style="color:'
                        row += dorf.entry['allyfarbe'] +';">'
                        if dorf.entry['rittername'] != ".":
                            row += dorf.entry['rittername'][0:3]
                        elif config.is_kraehe() and terrain.entry["typ"]:
                            row += "." * terrain.entry["typ"]
                        elif config.is_kraehe():
                            row += "_"
                        else:
                            row += "."
                        row += '</div>'
                    elif show_armeen:
                        row += '<div>&nbsp;</div>'
                    if show_armeen:
                        row += '<div class="armeen">'
                        row += '<span></span>' # dummy fuer Formatierung
                        if armee.has(x,y):
                            for entry in armee.get(x,y):
                                row += '<span style="background-color:'
                                row += entry["allyfarbe"] + '"></span>'
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
