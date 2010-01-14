#!/usr/bin/python
"""Modul um die Karte anzuzeigen und eine Kartenuebersicht zu generieren"""

#import cgitb
#cgitb.enable()

import config
import ausgabe
import util
from types import StringType

viel_armeen = 8
"""Gibt an ab welcher Armeezahl auf einem Feld weniger Infos gezeigt werden"""

def print_link(link, name, br=False):
    """Gibt eine bestimmten Kartenlink aus.
    
    @param link: Der Teil der URL nach C{/show/karte}
    @param name: Der Linktext
    @param br: ob ein C{BR} davorgesetzt werden soll
    @type br: C{BooleanType}
    """

    print ausgabe.link("/show/karte"+link, name, br=br)

def print_area_link(area, levels, name, br=False):
    """Gibt mehrere Levellinks fuer ein bestimmtes Gebiet aus.

    @param area: Der Gebietsbezeichner
    @param levels: Liste mit Untergrund-Leveln, Bsp.: C{[1,2,3]}
    @param name: Der angezeigte Name des Gebiets
    @param br: ob ein C{BR} davorgesetzt werden soll
    @type br: C{BooleanType}
    """

    if area != "":
        area = "/" + area
    print_link(area, name, br=br);
    for level in levels:
        link = area + "/u" + str(level)
        new_name = name + " Level U" + str(level)
        print_link(link, new_name, br=True)
    print "<br />"

def list_maps():
    """Gibt die verfuegbaren Kartenlinks in einer Tabelle aus."""

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
    print_area_link("", [1,2,3,4],      "komplett (Normalgroesse)", br=True)
    print_link("/clean",        "komplett (ohne Doerfer)", br=True)
    print_link("/small",        "komplett (kleine Felder)", br=True)
    print_link("/clean/small",  "komplett (klein ohne Doerfer)", br=True)
    print_link("/verysmall",    "komplett (sehr kleine Felder)", br=True)
    print_link("/tiny",         "komplett (winzige Felder)", br=True)
    print '<br />'
    print_link("/neu", "aktuelle Doerfer (6 Monate)", br=True)
    print '</td><td class="karten">'
    print_area_link("osten", [1,2,3,4], "Der Osten")
    print_area_link("westen", [1,2,3],  "Der Westen", br=True)
    print_area_link("sueden", [1,2,3],  "Der Sueden", br=True)
    print '</td><td class="karten">'
    print "(Piraten)"
    print_area_link("drache", [1,2],    "Drachenhoehle", br=True)
    print "<br />(Zentral)"
    print_area_link("axt", [1,2,3],     "Axtwaechterquest", br=True)
    print "<br />(K&uuml;ste)"
    print_area_link("schuetzen", [1],   "Meisterschuetzenquest", br=True)
    print '</td></tr></table>'
    print '</div>'

def nav_link(text, direction=None, amount=0):
    """Gibt eine Navigationslink zurueck.

    @param direction: Ist C{"nord"}, C{"sued"}, C{"ost"} oder C{"west"}.
    @param amount: Die Schrittweite
    @type amount: C{IntType}
    @param text: Der Linktext
    @return: Der HTML-Link
    @rtype: C{StringType}
    """

    x1 = int(form["x1"].value); x2 = int(form["x2"].value)
    y1 = int(form["y1"].value); y2 = int(form["y2"].value)
    if direction is not None:
        if direction == "nord":
            y1 -= amount; y2 = y1 + 21;
        elif direction == "sued":
            y2 += amount; y1 = y2 - 21;
        elif direction == "ost":
            x1 -= amount; x2 = x1 + 33;
        elif direction == "west":
            x2 += amount; x1 = x2 - 33;
    link = '/show/karte/'
    link += str(x1) + '.' + str(y1) + '-' + str(x2) + '.' + str(y2)
    if level != 'N':
        link += '/' + level
    if "armeen" in layer and "doerfer" not in layer:
        link += '/armeen'
    elif "armeen" not in layer and "doerfer" in layer:
        link += '/doerfer'
    elif "armeen" not in layer and "doerfer" not in layer:
        link += '/clean'
    if "size" in form and form["size"].value != "normal":
        link += '/' + form["size"].value
    return ausgabe.link(link, text)

def level_link(direction):
    """Gibt eine Level-link zurueck.

    Linktext ist das Ziellevel.
    @param direction: Ist C{"hoch"} oder C{"runter"}
    @return: Der HTML-Link
    @rtype: C{StringType}
    """

    x1 = int(form["x1"].value); x2 = int(form["x2"].value)
    y1 = int(form["y1"].value); y2 = int(form["y2"].value)
    if ((direction == "hoch" and level != 'N')
            or (direction == "runter" and level != 'u5')):
        link = '/show/karte/'
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
        if "armeen" in layer and "doerfer" not in layer:
            link += '/armeen'
        elif "armeen" not in layer and "doerfer" in layer:
            link += '/doerfer'
        elif "armeen" not in layer and "doerfer" not in layer:
            link += '/clean'
        if "size" in form and form["size"].value != "normal":
            link += '/' + form["size"].value
        return ausgabe.link(link, new_level)
    else:
        return '&nbsp;'

def __escape(var):
    """Escape eine Variable fuer die javascript Detailansicht

    @param var: Eingabevariable
    @rtype: wie Eingabe
    """
    if type(var) is StringType:
        # &vbar; ist keine Standard HTML-Entity
        # damit sie wirklich nicht als "|" interpretiert wird
        escaped = var.replace("|", "&vbar;")
        escaped = escaped.replace("'", "\\'")
        escaped = escaped.replace('"', "&quot;")
        return escaped
    else:
        return var

def __format(var):
    """Formatierte Ausgabe einer Variable

    @param var: Eingabevariable
    @return: C{"?"} bei None, sonst C{str(var)}
    @rtype: C{StringType}
    """
    if var == None:
        return "?"
    else:
        return __escape(str(var))


# Aufruf direkt: Karten anzeigen
if __name__ == '__main__':
    import cgi
    from terrain import Terrain
    from dorf import Dorf
    from armee import Armee

    form = cgi.FieldStorage()

    if "list" in form:
        title = "Kr&auml;henkarten"
    else:
        title = "Kr&auml;henkarte"
    print 'Content-type: text/html; charset=utf-8\n'
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
    print '          "http://www.w3.org/TR/html4/loose.dtd">'
    print '<html><head>'
    print '<title>' + title + '</title>'
    print '<meta name="robots" content="noindex, nofollow">'
    print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
    print '<meta http-equiv="expires" content="0">'
    print '<link rel="stylesheet" type="text/css" href="',
    print ausgabe.prefix + '/show/stylesheet">'
    if config.is_kraehe() or (config.is_tw() and config.is_tester()):
        print '<script src="' + ausgabe.prefix + '/show/javascript"',
        print 'type="text/javascript"></script>'
    print '</head>\n'
    print '<body>\n'

    if "list" in form:
        print '<h1>' + title + '</h1>'
        list_maps()
    else:
        # Zeige eine Karte


        # Bereite Layer und Bereiche vor
        if "level" in form:
            level = form["level"].value
        else:
            level = 'N'

        if "layer" in form:
            layer = form["layer"].value.split()
        else:
            layer = []

        allow_dorf = True # zur Zeit keine Ausnahmen
        if not allow_dorf or level != "N" or "doerfer" not in layer:
            show_dorf = False
        else:
            show_dorf = True
            dorf = Dorf()
            if form["layer"].value == "neu":
                dorf.set_add_cond("datediff(now(), aktdatum) < 180")
            dorf.fetch_data()

        if config.is_kraehe():
            allow_armeen = True
        elif config.is_tw() and config.is_tester():
            allow_armeen = True
        else:
            allow_armeen = False

        if allow_armeen and "armeen" in layer:
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


        # Bereite Formatierungen vor
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
        if fontsize <= 8:
            show_armeen = False
            allow_armeen = False
        if fontsize == 0:
            show_dorf = False
            allow_dorf = False

        print '<style type="text/css">'
        print '#karte {'
        print '    table-layout:fixed;'
        print '    margin:0px;'
        print '    border-collapse:collapse;'
        print '}'
        print '#karte tr td {'
        print '    padding:0px;'
        print '    height: ' + str(size) + 'px;'
        print '    width: ' + str(size) + 'px;'
        print '    background-repeat:no-repeat;'
        print '    font-size: ' + str(fontsize) + 'pt;'
        print '    text-align:center;'
        print '}'
        print 'div.armeen {'
        print '    margin-left: ' + str(fontsize-5) + 'px;'
        print '    text-align:left;'
        print '    max-height: ' + str(fontsize-5) + 'px;'
        print '}'
        print 'span.armee_dark {'
        print '    display: inline-block;'
        if fontsize > 8:
            print '    height: ' + str(fontsize-5) + 'px;'
            print '    width: ' + str(fontsize-5) + 'px;'
            print '    border: 1px solid white;'
        else:
            print '    height: 0px;'
            print '    width: 0px;'
        print '}'
        print 'span.armee_bright {'
        print '    display: inline-block;'
        if fontsize > 8:
            print '    height: ' + str(fontsize-5) + 'px;'
            print '    width: ' + str(fontsize-5) + 'px;'
            print '    border: 1px solid black;'
        else:
            print '    height: 0px;'
            print '    width: 0px;'
        print '}'
        print 'span.dark {'
        print '    border: 1px solid white;'
        print '}'
        print 'span.bright {'
        print '    border: 1px solid black;'
        print '}'
        print 'a.dark, td.dark {'
        print '    text-shadow: white 1px 1px 1px,  white -1px -1px 1px,',
        print ' white -1px 1px 1px, white 1px -1px 1px;'
        print '}'
        print 'a.bright, td.bright {'
        print '    text-shadow: black 1px 1px 1px,  black -1px -1px 1px,',
        print ' black -1px 1px 1px, black 1px -1px 1px;'
        print '}'
        print 'table.detail tr td, #dorfdetail, #armeedetail {'
        print '    font-size:9pt;'
        print '    background-color:#333333;'
        print '}'
        print 'table.navi tr td {'
        print '    text-align:center;'
        print '}'
        print 'td.navi, div.navi{'
        if int(form["x2"].value) >= 999:
            print '    background-color:#333333;'
        print '    font-weight:bold;'
        print '    font-size:12pt;'
        print '}'
        print '</style>\n'

        # Detailboxen
        if config.is_kraehe() or (config.is_tw() and config.is_tester()):
            # Dorfdetail / Koordinateninfo (deshalb immer)
            print '<div id="dorfdetail" style="z-index:2; position:fixed;',
            print 'top:5px; left:38px; width:85em;',
            print 'padding:5px;"><div>&nbsp;</div></div>'
            print '<br /><div></div>'
            if show_armeen:
                # Armeedetail
                print '<div id="armeedetail" style="z-index:2; position:fixed;',
                print 'top:170px; right:5px; width:13em; min-height:10em;',
                print 'font-size:9pt; background-color:#333333;',
                print 'padding:5px;"><div>&nbsp;</div></div>'

        # Kartennavigation
        print '\n<table class="navi"',
        print ' style="z-index:2; position:fixed; top:35px; right:60px;">'
        if int(form["x2"].value) < 999:
            # Richtungen
            print '<tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('&uArr;', 'nord', 17)
            print '</td></tr><tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('&uarr;', 'nord', 3)
            print '</td></tr><tr>'
            print '<td class="navi">' + nav_link('&lArr;', 'ost', 24) + '</td>'
            print '<td class="navi">' + nav_link('&larr;', 'ost', 4) + '</td>'
            print '<td>'
            if config.is_kraehe():
                print ausgabe.link("/show/karte/kraehen", "&bull;")
            elif config.is_tw():
                print ausgabe.link("/show/karte/osten", "&bull;")
            print '</td>',
            print '<td class="navi">' + nav_link('&rarr;', 'west', 4) + '</td>'
            print '<td class="navi">' + nav_link('&rArr;', 'west', 24) + '</td>'
            print '</tr><tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('&darr;', 'sued', 3)
            print '</td></tr><tr><td></td><td></td>'
            print '<td class="navi">' + nav_link('&dArr;', 'sued', 17)
        else:
            print '<tr><td class="navi" colspan="3">'
            if config.is_kraehe():
                print ausgabe.link("/show/karte/kraehen", "HOME")
            elif config.is_tw():
                print ausgabe.link("/show/karte/osten", "HOME")
        print '</td></tr></table>'
        # Level
        print '<table class="navi"',
        print 'style="z-index:2; position:fixed; top:60px; right:5px;">'
        print '<tr><td></td><td></td><td class="navi">' + level_link("hoch")
        print '</td></tr>'
        print '<tr><td></td><td></td><td class="navi">' + level + '</td></tr>'
        print '<tr><td></td><td></td><td class="navi">' + level_link("runter")
        print '</td></tr>'
        print '</table>\n'

        if int(form["x2"].value) < 999: # nicht fuer Vollkarte
            print '<div style="z-index:2; position:fixed;'
            print ' bottom:10px; right:20px;" class="navi">'
            # Armeeschalter
            if show_armeen:
                print '<input type="checkbox" checked="checked"',
                print 'id="armeeschalter"',
                print 'onClick="javascript:toggleArmeen()" />',
                print 'Armeen<br />'
            elif allow_armeen:
                layer.append("armeen")
                print nav_link("+ Armeen") + "<br />"
                layer.remove("armeen")
            # Dorfschalter
            if show_dorf:
                print '<input type="checkbox" checked="checked"',
                print 'id="dorfschalter"',
                print 'onClick="javascript:toggleDorf()" />',
                print 'D&ouml;rfer<br />'
            elif allow_dorf:
                layer.append("doerfer")
                print nav_link("+ D&ouml;rfer") + "<br />"
                layer.remove("doerfer")
            # zeige wieder alles
            if allow_dorf and allow_armeen and not (show_armeen or show_dorf):
                layer += ["armeen", "doerfer"]
                print nav_link("+ Beides") + "<br />"
                layer.remove("doerfer")
                layer.remove("armeen")
            print "<br />"
            # zurueck zum Datenbankindex
            if config.is_kraehe():
                print ausgabe.link("/show", "Index")
            else:
                print ausgabe.link("/show/karten", "Index")
            print '</div>'

        #
        # Die eigentliche Karte
        #
        width = size * (terrain.xmax - terrain.xmin + 1 + 2)
        print '\n\n<table id="karte" style="width:' + str(width) + 'px;">'
        print '<tr style="height:' + str(size) + 'px;"><td></td>'
        # X - Achse
        for x in range(terrain.xmin, terrain.xmax + 1):
            print '<td>' + str(x) + '</td>'
        for y in range(terrain.ymin, terrain.ymax + 1):
            # Y - Achse
            print '<tr style="height:' + str(size) + 'px;">'
            print '<td>' + str(y)  + '</td>'
            for x in range(terrain.xmin, terrain.xmax + 1):
                if terrain.has(x,y): # Kartenbereich

                    # Terrainhintergrund
                    terrain.get(x,y)
                    row = '<td style="background-image:url(/img/terrain/'
                    row += str(size) + '/' + terrain.entry["terrain"]
                    row += '.gif)'
                    if show_dorf and not config.is_kraehe() and dorf.has(x,y):
                        row += '; color:'
                        row += dorf.get(x,y)['allyfarbe']
                    row += ';"' # style attribut auf jeden Fall zumachen
                    if show_dorf and not config.is_kraehe() and dorf.has(x,y):
                        if util.brightness(dorf.get(x,y)['allyfarbe']) < 55:
                            row += ' class="dark"'
                        else:
                            row += ' class="bright"'

                    # Detail-Mouse-Over
                    if config.is_kraehe() or (config.is_tw() and config.is_tester()):
                        row += ' onmouseover="showPos(\''
                        row += str(x) + "," + str(y)
                        if config.is_kraehe() and terrain.entry["typ"]:
                            row += " " + "." * terrain.entry["typ"]
                        # fuer Dorf
                        if show_dorf and dorf.has(x,y):
                            dorf.get(x,y)
                            list = []
                            for col in ['rittername', 'alliname', 'dorfname',
                                    'dorflevel', 'mauer', 'aktdatum']:
                                list.append(__format(dorf.entry[col]))
                            list = '|' + '|'.join(list)
                        else:
                            list = '|?' * 6
                        # fuer Armeen
                        if show_armeen and armee.has(x,y):
                            armee.get(x,y)
                            # Anzahl Infos pro Armee
                            if len(armee.entry) < viel_armeen:
                                list += '|7'
                            else:
                                list += '|4'
                            # Armeen anhaengen
                            for entry in armee.entry:
                                list += '|' + __escape(entry["allyfarbe"])
                                if (entry["rittername"] == "Keiner"
                                        and len(armee.entry) >= viel_armeen):
                                    list += '|' + __escape(entry["name"])
                                else:
                                    list += '|' + __escape(entry["rittername"])
                                list += '|' + __format(entry["size"])
                                list += '|' + __format(entry["strength"])
                                # mehr Infos bei wenigen Armeen
                                if len(armee.entry) < viel_armeen:
                                    list += '|(' + __escape(entry["name"]) + ')'
                                    list += '|' + __format(entry["ap"])
                                    list += '|' + __format(entry["bp"])
                        if ((show_dorf and dorf.has(x,y))
                                or (show_armeen and armee.has(x,y))):
                            row += list
                        row += '\')" onmouseout="delPos()"'
                    row += '>'

                    # Detail-Link
                    if not config.is_kraehe():
                        show_detail_link = False
                    elif show_armeen and armee.has(x,y):
                        show_detail_link = True
                    elif (show_dorf and dorf.has(x,y)
                            and dorf.get(x,y)["rittername"] != "."):
                        show_detail_link = True
                    else:
                        show_detail_link = False
                    if show_detail_link:
                        row += '<a href="' + ausgabe.prefix + '/show/feld/'
                        row += str(x) + '.' + str(y)
                        if level != "N":
                            row += '/' + level
                        row += '"'
                        if show_dorf and dorf.has(x,y):
                            dorf.get(x,y)
                            row += ' style="color:' + dorf.entry['allyfarbe']
                            if util.brightness(dorf.entry['allyfarbe']) < 55:
                                row += ';" class="dark"'
                            else:
                                row += ';" class="bright"'
                        row += ' target="_blank">'

                    # Dorf
                    if show_dorf and dorf.has(x,y):
                        dorf.get(x,y)
                        row += '<div class="dorf">'
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
                        # Platzhalter fuer Dorf
                        row += '<div>&nbsp;</div>'

                    # Armeen
                    if show_armeen:
                        row += '<div class="armeen">'
                        if armee.has(x,y):
                            for entry in armee.get(x,y):
                                if util.brightness(entry["allyfarbe"]) < 55:
                                    row += '<span class="armee_dark"'
                                else:
                                    row += '<span class="armee_bright"'
                                row += ' style="background-color:'
                                row += entry["allyfarbe"] + ';"></span>'
                        row += '</div>'
                    if show_detail_link:
                        row += '</a>'
                    row += '</td>'
                    print row
                else: # not terrain.has(x,y):
                    print '<td></td>'
            # y - Achse
            print '<td>' + str(y) + '</tr>'
        # X - Achse
        print '<tr style="height:' + str(size) + 'px;"><td></td>'
        for x in range(terrain.xmin, terrain.xmax + 1):
            print '<td>' + str(x) + '</td>'
        print '</table>'

    print "\n</body></html>"

# vim:set shiftwidth=4 expandtab smarttab:
