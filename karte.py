#!/usr/bin/env python
"""Modul um die Karte anzuzeigen und eine Kartenuebersicht zu generieren"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import ausgabe
import util
from types import StringType
import os

viel_armeen = 8
"""Gibt an ab welcher Armeezahl auf einem Feld weniger Infos gezeigt werden"""

def nav_link(x1, y1, x2, y2, level, text, direction=None, amount=0,
        layer=["armeen", "doerfer"], size="normal"):
    """Gibt eine Navigationslink zurueck.

    @param direction: Ist C{"nord"}, C{"sued"}, C{"ost"} oder C{"west"}.
    @param amount: Die Schrittweite
    @type amount: C{IntType}
    @param text: Der Linktext
    @return: Der HTML-Link
    @rtype: C{StringType}
    """

    if size == "tiny":
        x_width = 300; y_width = 200;
    elif size == "verysmall":
        x_width = 200; y_width = 90;
    elif size == "small":
        x_width = 66; y_width = 42;
    else:
        x_width = 31; y_width = 21;

    if direction is not None:
        if direction == "nord":
            y1 -= amount; y2 = y1 + y_width;
        elif direction == "sued":
            y2 += amount; y1 = y2 - y_width;
        elif direction == "ost":
            x1 -= amount; x2 = x1 + x_width;
        elif direction == "west":
            x2 += amount; x1 = x2 - x_width;
        elif direction == "center":
            x1 -= x_width//2; y1 -= y_width//2;
            x2 += x_width//2 + 1; y2 += y_width//2 + 1;

    link = '/show/karte/'
    link += str(x1) + '.' + str(y1) + '-' + str(x2) + '.' + str(y2)
    if level != 'N':
        link += '/' + level
    if not (len(layer) == 2 and "armeen" in layer and "doerfer" in layer):
        link += '/' + "+".join(layer)
    if size != "normal":
        link += '/' + size
    return ausgabe.link(link, text)

def __nav_link(text, direction=None, amount=0):
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
    if "size" in form:
        size = form["size"].value
        return nav_link(x1, y1, x2, y2, level, text, direction, amount,
                layer, size)
    else:
        return nav_link(x1, y1, x2, y2, level, text, direction, amount, layer)

def center_link(x, y, level="N", text="zur Karte"):
    """Erstellt einen Kartenlink fuer eine Koordinate

    @return: HTML-Link
    @rtype: C{StringType}
    """
    layer = ["armeen", "doerfer"] # + center spaeter
    return nav_link(x, y, x, y, level, text, "center", 0, layer)

def level_link(direction):
    """Gibt einen Level-link zurueck.

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
        if not (len(layer) == 2 and "armeen" in layer and "doerfer" in layer):
            link += '/' + "+".join(layer)
        if "size" in form and form["size"].value != "normal":
            link += '/' + form["size"].value
        return ausgabe.link(link, new_level)
    else:
        return '&nbsp;'

def __print_navi(cross=False):
    """Gibt die Kartennavigation aus

    @param cross: Ob das Richtungskreuz gezeigt werden soll
    @type cross: C{BooleanType}
    """

    print '\n<table class="navi"',
    print ' style="z-index:2; position:fixed; top:35px; right:60px;">'
    if cross:
        # Richtungen
        print '<tr><td></td><td></td>'
        print '<td class="navi">' + __nav_link('&uArr;', 'nord', 17)
        print '</td></tr><tr><td></td><td></td>'
        print '<td class="navi">' + __nav_link('&uarr;', 'nord', 3)
        print '</td></tr><tr>'
        print '<td class="navi">' + __nav_link('&lArr;', 'ost', 24) + '</td>'
        print '<td class="navi">' + __nav_link('&larr;', 'ost', 4) + '</td>'
        print '<td>'
        print "<a href=\""+ os.environ["SCRIPT_URL"] +"\">&bull;</a><br />"
        print '</td>',
        print '<td class="navi">' + __nav_link('&rarr;', 'west', 4) + '</td>'
        print '<td class="navi">' + __nav_link('&rArr;', 'west', 24) + '</td>'
        print '</tr><tr><td></td><td></td>'
        print '<td class="navi">' + __nav_link('&darr;', 'sued', 3)
        print '</td></tr><tr><td></td><td></td>'
        print '<td class="navi">' + __nav_link('&dArr;', 'sued', 17)
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
    if config.allow_hoehlen():
        print '<tr><td></td><td></td><td class="navi">' + level_link("runter")
        print '</td></tr>'
    print '</table>\n'

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

def __detail_link(x, y, level="N", color=None, new_window=True):
    """Startet den Detaillink.

    Nicht vergessen den Link wieder zu schliessen!

    @return: Start-Tag eines HTML-links
    @rtype: C{StringType}
    """
    text = '<a href="' + ausgabe.prefix + '/show/feld/'
    text += str(x) + '.' + str(y)
    if level != "N":
        text += '/' + level
    text += '"'
    if color is not None:
        text += ' style="color:' + color
        if util.brightness(color) < 55:
            text += ';" class="dark"'
        else:
            text += ';" class="bright"'
    if new_window:
        text += ' target="_blank">'
    else:
        text += '>'
    return text

def __dorf(dorf, x, y, terrain=None):
    """Kartenanzeige eines Dorfes
    
    @return: Dorf-DIV (HTML)
    @rtype: C{StringType}
    """

    dorf.get(x,y)
    text = '<div class="dorf">'
    if dorf.entry['rittername'] != ".":
        # translate(None, "<>"),  None erst ab python 2.6
        text += dorf.entry['rittername'].replace("<", "").replace(">", "")[0:3]
    elif terrain is not None and config.is_kraehe() and terrain.entry["typ"]:
        text += "." * terrain.entry["typ"]
    elif config.is_kraehe():
        text += "_"
    else:
        text += "."
    text += '</div>'
    return text

def __armeen(armee, x, y):
    """Kartenanzeige von Armeen auf einem Feld

    @return: Armee-DIV (HTML)
    @rtype: C{StringType}
    """

    text = '<div class="armeen">'
    if armee.has(x,y):
        for entry in armee.get(x,y):
            if util.brightness(entry["allyfarbe"]) < 55:
                text += '<span class="armee_dark"'
            else:
                text += '<span class="armee_bright"'
            text += ' style="background-color:'
            text += __format(entry["allyfarbe"]) + ';"></span>'
    text += '</div>'
    return text

def create_styles(size, fontsize,
        show_armeen=True, show_dorf=True, background=False):
    """erstellt ein passendes Stylesheet
    """

    text = '#karte tr td {\n'
    text += '    padding:0px;\n'
    text += '    height: ' + str(size) + 'px;\n'
    text += '    width: ' + str(size) + 'px;\n'
    text += '    background-repeat:no-repeat;\n'
    text += '    font-size: ' + str(fontsize) + 'pt;\n'
    text += '    text-align:center;\n'
    text += '}\n'
    text += 'div.armeen {\n'
    text += '    margin-left: ' + str(fontsize-5) + 'px;\n'
    if show_armeen and not show_dorf:
        text += '    margin-top:5px;\n'
    text += '    text-align:left;\n'
    text += '    max-height: ' + str(fontsize-5) + 'px;\n'
    text += '}\n'
    text += 'span.armee_dark {\n'
    text += '    display: inline-block;\n'
    if fontsize > 8:
        text += '    height: ' + str(fontsize-5) + 'px;\n'
        text += '    width: ' + str(fontsize-5) + 'px;\n'
        text += '    border: 1px solid white;\n'
    else:
        text += '    height: 0px;\n'
        text += '    width: 0px;\n'
    text += '}\n'
    text += 'span.armee_bright {\n'
    text += '    display: inline-block;\n'
    if fontsize > 8:
        text += '    height: ' + str(fontsize-5) + 'px;\n'
        text += '    width: ' + str(fontsize-5) + 'px;\n'
        text += '    border: 1px solid black;\n'
    else:
        text += '    height: 0px;\n'
        text += '    width: 0px;\n'
    text += '}\n'
    text += 'td.navi, div.navi{\n'
    if background:
        text += '    background-color:#333333;\n'
    text += '    font-weight:bold;\n'
    text += '    font-size:12pt;\n'
    text += '}\n'
    return text

def small_map(x, y, level="N", sicht=2, imported=False):
    """Eine kleine integrierbare Karte

    vorher sollte L{create_styles<karte.create_styles>} abgesetzt werden

    @param x: Mittelpunkt X
    @type x: C{IntType}
    @param y: Mittelpunkt Y
    @type y: C{IntType}
    @param sicht: Sichtweite vom Mittelpunkt
    @type sicht: C{IntType}
    @param imported: Karte wird woanders integriert
    @type imported: C{BooleanType}
    """

    from dorf import Dorf
    from armee import Armee
    from terrain import Terrain

    size = 32 
    fontsize = 9

    xmin = x - sicht; xmax = x + sicht
    ymin = y - sicht; ymax = y + sicht

    if level == "N" and config.allow_doerfer(message=False):
        dorf = Dorf()
        dorf.fetch_data(xmin, xmax, ymin, ymax)
        show_doerfer = True
    else:
        show_doerfer = False

    if config.allow_armeen(message=False):
        armee = Armee()
        armee.fetch_data(level, xmin, xmax, ymin, ymax)
        show_armeen = True
    else:
        show_armeen = False

    terrain = Terrain()
    terrain.fetch_data(level, xmin, xmax, ymin, ymax)

    if imported:
        achsen = False
        new_window = True
    else:
        achsen = True
        new_window = False

    if achsen:
        width = size * (sicht + 2)
    else:
        width = size * (sicht)
    karte = '\n\n<table id="karte" style="width:' + str(width) + 'px;">\n'
    if achsen:
        # X - Achse
        karte += '<tr style="height:' + str(size) + 'px;"><td></td>\n'
        for x in range(xmin, xmax + 1):
            karte += '<td>' + str(x) + '</td>\n'
        karte += '</tr>\n'
    for y in range(ymin, ymax + 1):
        karte += '<tr style="height:' + str(size) + 'px;">\n'
        if achsen:
            # Y - Achse
            karte += '<td>' + str(y)  + '</td>\n'
        for x in range(xmin, xmax + 1):
            if terrain.has(x,y): # Kartenbereich
                terrain.get(x,y)
                if show_doerfer and dorf.has(x,y):
                    color = dorf.get(x,y)['allyfarbe']
                else:
                    color = None

                row = '<td style="background-image:url(/img/terrain/'
                row += str(size) + '/' + terrain.entry["terrain"]
                row += '.gif);'
                if color and not config.is_kraehe():
                    row += ' color:' + color + ';"'
                    if util.brightness(color) < 55:
                        row += ' class="dark">'
                    else:
                        row += ' class="bright">'
                else:
                    row += '">'

                detail_link = False
                if config.is_kraehe():
                    if (show_doerfer and dorf.has(x,y)
                            and dorf.get(x,y)["rittername"] != "."):
                        row += __detail_link(x, y, level, color, new_window)
                        detail_link = True
                    elif show_armeen and armee.has(x,y):
                        row += __detail_link(x, y, level, color, new_window)
                        detail_link = True

                if show_doerfer and dorf.has(x,y):
                    row += __dorf(dorf, x, y, terrain)
                if show_armeen:
                    row += __armeen(armee, x, y)

                if detail_link: row += '</a>'
                row += '</td>\n'
                karte += row
            else:
                karte += '<td></td>\n'
        if achsen:
            # y - Achse
            karte += '<td>' + str(y) + '</td>'
        karte += '</tr>\n'
    if achsen:
        # X - Achse
        karte += '<tr style="height:' + str(size) + 'px;"><td></td>\n'
        for x in range(xmin, xmax + 1):
            karte += '<td>' + str(x) + '</td>\n'
        karte += '</tr>\n'
    karte += '</table>\n'
    return karte


# Aufruf direkt: Karten anzeigen
# mod_python.cgihandler doesn't count as direct
#if __name__ == '__main__':
if True:
    import cgi
    from terrain import Terrain
    from dorf import Dorf
    from armee import Armee

    form = cgi.FieldStorage()

    if "list" in form:
        title = "Kr&auml;henkarten"
    else:
        title = "Kr&auml;henkarte"

    if "HTTP_IF_MODIFIED_SINCE" in os.environ:
        cache_string = os.environ["HTTP_IF_MODIFIED_SINCE"]
        db_string = util.map_last_modified_http(
                config.allow_doerfer(message=False),
                config.allow_armeen(message=False))
        if db_string == cache_string:
            is_still_valid = True
        else:
            is_still_valid = False
    else:
        is_still_valid = False

    if is_still_valid:
        print 'Status: 304 Not Modified\n'
    else:
        if "sicht" not in form or config.importkarte:
            # kein Last-Modified fuer deaktivierte Importkarte
            print 'Last-Modified: ' + util.map_last_modified_http(
                    config.allow_doerfer(message=False),
                    config.allow_armeen(message=False))
        print 'Cache-Control: no-cache,must-revalidate'
        print 'Content-type: text/html; charset=utf-8\n'
        print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"'
        print '          "http://www.w3.org/TR/html4/loose.dtd">'
        print '<html><head>'
        print '<title>' + title + '</title>'
        print '<meta name="robots" content="noindex, nofollow">'
        print '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
        print '<link rel="stylesheet" type="text/css" href="',
        print ausgabe.prefix + '/show/stylesheet">'
        print '<script src="' + ausgabe.prefix + '/show/javascript"',
        print 'type="text/javascript"></script>'
        print '</head>\n'
        print '<body>\n'

        if "list" in form:
            print '<h1>' + title + '</h1>'
            list_maps()
        elif "sicht" in form:
            if config.importkarte:
                print '<style type="text/css">'
                print create_styles(32, 9)#, show_armeen, show_dorf, background)
                print 'body { margin:0px; }'
                print '</style>\n'
                print small_map(int(form["x"].value), int(form["y"].value),
                        form["level"].value, int(form["sicht"].value),
                        imported=True)
            else:
                msg = "Importkarte deaktiviert"
                util.print_error_message(msg) 
        else:
            # Zeige eine Karte


            # Bereite gewuenschte Layer und Bereiche vor
            if "level" in form and config.allow_hoehlen():
                level = form["level"].value
            else:
                level = 'N'

            if "layer" in form:
                layer = form["layer"].value.split()
                for item in layer:
                    while layer.count(item) > 1:
                        layer.remove(item)
                if len(layer) > 1 and "clean" in layer:
                    layer.remove("clean")
                if len(layer) == 1 and "neu" in layer:
                    layer.append("armeen")
                    layer.append("doerfer")
                if len(layer) == 1 and "alt" in layer:
                    layer.append("armeen")
            else:
                layer = []

            # bestimme was grundsaetzlich erlaubt ist
            allow_dorf = config.allow_doerfer(floating_message=True)
            allow_armeen = config.allow_armeen(floating_message=True)
            allow_details = config.allow_details(floating_message=True)
            allow_target = config.allow_target()

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

            # entferne unpassende Layer
            if fontsize <= 8:
                allow_armeen = False
                if "armeen" in layer:
                    layer.remove("armeen")
            if fontsize == 0 or level != "N":
                allow_dorf = False
                if "doerfer" in layer:
                    layer.remove("doerfer")
            if len(layer) == 0:
                # dummy layer der fuer "nichts" steht
                layer.append("clean")


            # bestimme was wirklich gezeigt wird

            if "x2" in form:
                bounding_box = config.bounding_box()
                xmin = max(bounding_box.x1, int(form["x1"].value))
                ymin = max(bounding_box.y1, int(form["y1"].value))
                xmax = min(bounding_box.x2, int(form["x2"].value))
                ymax = min(bounding_box.y2, int(form["y2"].value))

            if allow_armeen and "armeen" in layer:
                show_armeen = True
                armee = Armee()
                if "alt" in layer:
                    armee.replace_cond("TRUE") # keine Bedingung
                elif "neu" in layer:
                    armee.set_add_cond("hour(timediff(now(), last_seen)) < 6")
                if "x1" in form:
                    armee.fetch_data(level, xmin, xmax, ymin, ymax)
                else:
                    armee.fetch_data(level)
            else:
                show_armeen = False

            terrain = Terrain()
            if "x2" in form:
                bounding_box = config.bounding_box()
                if int(form["x2"].value) >= 999 and show_armeen:
                    real_x1 = max(bounding_box.x1, armee.xmin-15)
                    real_y1 = max(bounding_box.y1, armee.ymin-10)
                    real_x2 = min(bounding_box.x2, armee.xmax+15)
                    real_y2 = min(bounding_box.y2, armee.ymax+10)
                else:
                    real_x1 = max(bounding_box.x1, int(form["x1"].value))
                    real_y1 = max(bounding_box.y1, int(form["y1"].value))
                    real_x2 = min(bounding_box.x2, int(form["x2"].value))
                    real_y2 = min(bounding_box.y2, int(form["y2"].value))
                terrain.fetch_data(level, real_x1, real_x2, real_y1, real_y2)
            else:
                terrain.fetch_data(level, bounding_box.x1, bounding_box.x2,
                                            bounding_box.y1, bounding_box.y2)

            if not allow_dorf or "doerfer" not in layer:
                show_dorf = False
            else:
                show_dorf = True
                dorf = Dorf()
                if "neu" in layer:
                    add_cond = "datediff(now(), aktdatum) < "+str(config.tage_neu)
                    dorf.set_add_cond(add_cond)
                if "x2" in form:
                    dorf.fetch_data(real_x1, real_x2, real_y1, real_y2)
                else:
                    dorf.fetch_data()


            # Formatierungen
            background = int(form["x2"].value) >= 999
            print '<style type="text/css">'
            print create_styles(size, fontsize, show_armeen, show_dorf, background)
            print '</style>\n'

            # Detailboxen
            if allow_details:
                # Dorfdetail / Koordinateninfo (deshalb immer)
                print '<div id="dorfdetail" style="z-index:2; position:fixed;',
                print 'top:5px; left:38px; width:85em;',
                print 'padding:5px;"><div>&nbsp;</div></div>'
                print '<br /><div></div>'
                if show_armeen:
                    # Armeedetail
                    print '<div id="armeedetail" style="z-index:2; position:fixed;',
                    print 'top:170px; right:5px; width:15em; min-height:10em;',
                    print 'font-size:9pt; background-color:#333333;',
                    print 'padding:5px;"><div>&nbsp;</div></div>'

            # Kartennavigation
            cross = int(form["x2"].value) < 999
            __print_navi(cross)

            # Schalter
            print '<div style="z-index:2; position:fixed;'
            print ' bottom:10px; right:20px;" class="navi">'
            # Soft-Reload
            print "<a href=\""+ os.environ["SCRIPT_URL"] +"\">Soft-Reload</a><br />"
            print "<br />"
            # Neu-Schalter
            print "Zeige:<br />"
            if "neu" in layer:
                layer.remove("neu")
                print __nav_link('  Alle'),
                print '<span style="color:green">Neue</span><br />'
                layer.append("neu")
            else:
                layer.append("neu")
                print '<span style="color:green">Alle</span>',
                print __nav_link("  Neue") + "<br />"
                layer.remove("neu")
            # Armeeschalter
            if show_armeen:
                print '<input type="checkbox" checked id="armeeschalter"',
                print 'onclick="toggleArmeen()" />',
                print '<span style="color:green">Armeen</span><br />',
            elif allow_armeen:
                layer.append("armeen")
                print __nav_link("+ Armeen") + "<br />"
                layer.remove("armeen")
            # Dorfschalter
            if show_dorf:
                print '<input type="checkbox" checked id="dorfschalter"',
                print 'onclick="toggleDorf()" />',
                print '<span style="color:green">D&ouml;rfer</span><br />',
            elif allow_dorf:
                layer.append("doerfer")
                print __nav_link("+ D&ouml;rfer") + "<br />"
                layer.remove("doerfer")
            # zeige wieder alles
            if allow_dorf and allow_armeen and not (show_armeen or show_dorf):
                layer += ["armeen", "doerfer"]
                print __nav_link("+ Beides") + "<br />"
                layer.remove("doerfer")
                layer.remove("armeen")
            print "<br />"
            # zurueck zum Datenbankindex
            print ausgabe.link("/show", "Index")
            print '</div>'

            #
            # Die eigentliche Karte
            #
            is_kraehe = config.is_kraehe()
            width = size * (terrain.xmax - terrain.xmin + 1 + 2)
            print '\n\n<table id="karte" style="width:' + str(width) + 'px;">'
            print '<tr style="height:' + str(size) + 'px;"><td></td>'
            # X - Achse
            for x in range(terrain.xmin, terrain.xmax + 1):
                print '<td>' + str(x) + '</td>'
            for y in range(terrain.ymin, terrain.ymax + 1):
                print '<tr style="height:' + str(size) + 'px;">'
                print '<td>' + str(y)  + '</td>' # Y - Achse
                for x in range(terrain.xmin, terrain.xmax + 1):
                    if terrain.has(x,y): # Kartenbereich

                        # Terrainhintergrund
                        terrain.get(x,y)
                        row = '<td style="background-image:url(/img/terrain/'
                        row += str(size) + '/' + terrain.entry["terrain"]
                        row += '.gif)'
                        if show_armeen and not show_dorf:
                            row += '; vertical-align:top'
                        if show_dorf and not is_kraehe and dorf.has(x,y):
                            row += '; color:'
                            row += __format(dorf.get(x,y)['allyfarbe'])
                        if "abgang" in terrain.entry:
                            row += '; border: 1px solid red'
                        if "aufgang" in terrain.entry:
                            row += '; border: 1px solid green'
                        if "quest" in terrain.entry:
                            row += '; border: 1px solid yellow'
                        if allow_target and "ziel" in terrain.entry:
                            row += '; border: 1px solid blue'
                        row += ';"' # style attribut auf jeden Fall zumachen
                        if show_dorf and not is_kraehe and dorf.has(x,y):
                            if util.brightness(dorf.get(x,y)['allyfarbe']) < 55:
                                row += ' class="dark"'
                            else:
                                row += ' class="bright"'

                        # Detail-Mouse-Over
                        if allow_details:
                            row += ' onmouseover="showPos(\''
                            row += str(x) + "," + str(y)
                            if is_kraehe and terrain.entry["typ"]:
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
                                    if (entry["schiffstyp"] is not None
                                            and len(armee.entry) >= viel_armeen):
                                        list += '&br;['
                                        list += __escape(entry["schiffstyp"]) + ']'
                                    list += '|' + __format(entry["size"])
                                    list += '|' + __format(entry["strength"])
                                    # mehr Infos bei wenigen Armeen
                                    if len(armee.entry) < viel_armeen:
                                        list += '|(' + __escape(entry["name"]) + ')'
                                        if entry["schiffstyp"] is not None:
                                            list += '&br;['
                                            list += __escape(entry["schiffstyp"])
                                            list += ']'
                                        list += '|' + __format(entry["ap"])
                                        list += '|' + __format(entry["bp"])
                            if ((show_dorf and dorf.has(x,y))
                                    or (show_armeen and armee.has(x,y))):
                                row += list
                            row += '\')" onmouseout="delPos()"'
                        row += '>'

                        # Detail-Link
                        # != Details vom Mouse-Over
                        if not is_kraehe:
                            show_detail_link = False
                        elif show_armeen and armee.has(x,y):
                            show_detail_link = True
                        elif (show_dorf and dorf.has(x,y)
                                and dorf.get(x,y)["rittername"] != "."):
                            show_detail_link = True
                        else:
                            show_detail_link = False
                        if show_detail_link:
                            if show_dorf and dorf.has(x,y):
                                color = dorf.get(x,y)['allyfarbe']
                            else:
                                color = None
                            row += __detail_link(x, y, level, color)

                        # Dorf
                        if show_dorf and dorf.has(x,y):
                            row += __dorf(dorf, x, y, terrain)

                        # Armeen
                        if show_armeen:
                            row += __armeen(armee, x, y)
                        if show_detail_link:
                            row += '</a>'
                        row += '</td>'
                        print row
                    else: # not terrain.has(x,y):
                        print '<td></td>'
                # y - Achse
                print '<td>' + str(y) + '</td></tr>'
            # X - Achse
            print '<tr style="height:' + str(size) + 'px;"><td></td>'
            for x in range(terrain.xmin, terrain.xmax + 1):
                print '<td>' + str(x) + '</td>'
            print '</table>'

        print "\n</body></html>"

# vim:set shiftwidth=4 expandtab smarttab:
