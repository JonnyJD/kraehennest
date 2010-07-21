#!/usr/bin/env python
"""Modul um die Karte anzuzeigen und eine Kartenuebersicht zu generieren"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

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
        new_name = "U" + str(level)
        print_link(link, new_name)


def list_maps():
    """Gibt die verfuegbaren Kartenlinks in einer Tabelle aus."""

    # Skripte und Styles
    print \
"""
<style type="text/css">
    td.karten { width:34%; }
</style>

<script type="text/javascript">
    function genLink() {
        var form = document.getElementById("linkform");
        var x1 = form.x1.value;
        if (document.URL.indexOf("tw/show") != -1) {
            var link = "/tw/show/karte/";
        } else {
            var link = "/show/karte/";
        }
        link += form.x1.value + "." + form.x2.value + "-";
        link += form.y1.value + "." + form.y2.value;
        for (var i=0; i < form.level.length; i++)
            if (form.level[i].checked)
                level = form.level[i].value;
        if (level != "N")
            link += "/" + level;
        layer = new Array();
        for (var i=0; i < form.layer.length; i++)
            if (form.layer[i].checked)
                layer.push(form.layer[i].value);
        if (layer.length > 0) {
            layer = layer.join("+");
            if (layer != "armeen+doerfer")
                link += "/" + layer;
        }
        for (var i=0; i < form.size.length; i++)
            if (form.size[i].checked)
                size = form.size[i].value;
        if (size != "normal")
            link += "/" + size;

        var linkTD = document.getElementById("link");
        var linkTag = document.createElement("a");
        linkTag.href = link;
        linkTag.appendChild(document.createTextNode(link));
        linkTD.replaceChild(linkTag, linkTD.childNodes[1]);
    }
</script>
"""

    # Direktlinks
    print \
"""
<div class="box" style="clear:left;">
<h2>Karten</h2>
"""
    allow_armeen = config.allow_armeen()
    if config.is_kraehe():
        text = '<span style="font-weight:bold;">Kraehengebiet</span>'
        print_link("/kraehen", text)
    elif config.is_tw():
        text = '<span style="font-weight:bold;">Der Osten</span>'
        print_link("/osten", text)
    print '<br />'
    print_area_link("osten", [1,2,3,4], "Der Osten", br=True)
    print_area_link("westen", [1,2,3],  "Der Westen", br=True)
    print_area_link("sueden", [1,2,3],  "Der S&uuml;den", br=True)
    print '<br />'
    print_area_link("drache", [1,2],    "Drachenh&ouml;hle", br=True)
    print "(Piraten)"
    print_area_link("axt", [1,2,3],     "Axtw&auml;chterquest", br=True)
    print "(Zentral)"
    print_area_link("schuetzen", [1],   "Meistersch&uuml;tzenquest", br=True)
    print "(K&uuml;ste)"
    print '<br />'
    print_link("/doerfer", "komplette Dorfkarte", br=True)
    print_area_link("", [1,2,3,4], "komplett", br=True)
    if allow_armeen:
        print "(cut)"
        print_link("/armeen", "reine Armeekarte", br=True)
        print "(cut)"
    print_link("/clean", "Terrainkarte", br=True)
    for i in [1,2,3,4]:
        print_link("/u" + str(i) + "/clean", "U" + str(i))
    print '</div>'

    # Formular fuer individuelle Karte
    print \
"""
<div class="box">
<h2>Individualkarten</h2>
<form id="linkform" onclick="genLink()"><table>
<tr><td>Gebiet:&nbsp;</td><td colspan="2">
"""
    if config.is_kraehe():
      print \
"""
<input name="x1" type="text" size="3" maxlength="3" value="256">,
<input name="x2" type="text" size="3" maxlength="3" value="280">
&nbsp;&nbsp; - &nbsp;&nbsp;
<input name="y1" type="text" size="3" maxlength="3" value="289">,
<input name="y2" type="text" size="3" maxlength="3" value="303">
"""
    else:
      print \
"""
<input name="x1" type="text" size="3" maxlength="3" value="261">,
<input name="x2" type="text" size="3" maxlength="3" value="287">
&nbsp;&nbsp; - &nbsp;&nbsp;
<input name="y1" type="text" size="3" maxlength="3" value="292">,
<input name="y2" type="text" size="3" maxlength="3" value="322">
"""
    print """
</td></tr>
<tr><td>Level:&nbsp;</td><td colspan="2">
<input name="level" type="radio" value="N" checked>N
<input name="level" type="radio" value="u1">U1
<input name="level" type="radio" value="u2">U2
<input name="level" type="radio" value="u3">U3
<input name="level" type="radio" value="u4">U4
</td></tr>
<tr><td style="vertical-align:top;">Layer:&nbsp;</td><td>
"""
    if allow_armeen:
        print '<input name="layer" value="armeen" type="checkbox" checked>',
        print 'Armeen'
    print \
"""
<br /><input name="layer" value="doerfer" type="checkbox" checked> D&ouml;rfer
</td><td>
"""
    if allow_armeen:
        print '<input name="layer" value="alt" type="checkbox"> alt<br />'
    print \
"""
<input name="layer" value="neu" type="checkbox"> neu
</td></tr>
<tr><td style="vertical-align:top;">Gr&ouml;&szlig;e:&nbsp;</td><td>
<input name="size" type="radio" value="normal" checked> normal <br />
<input name="size" type="radio" value="small"> small
</td><td>
<input name="size" type="radio" value="verysmall"> verysmall <br />
<input name="size" type="radio" value="tiny"> tiny
</td></tr>
<tr><td colspan="3">
<input type="button" onclick="javascript:genLink()"'
value="generiere Link"></td></tr>
</table></form>

<br />Link:
<br /><div id="link">
"""
    if config.is_kraehe():
        print ausgabe.link("/show/karte/256.280-289.303")
    else:
        print ausgabe.link("/show/karte/261.287-292.322")
    print '</div>'
    print '</div>'


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
        if config.is_kraehe() or config.is_tw():
            # "Home" link
            if config.is_kraehe():
                link = "/show/karte/kraehen"
            elif config.is_tw():
                link = "/show/karte/osten"
            if (not (len(layer) == 2
                and "armeen" in layer and "doerfer" in layer)):
                link += '/' + "+".join(layer)
            print ausgabe.link(link, "&bull;")
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
            text += entry["allyfarbe"] + ';"></span>'
    text += '</div>'
    return text

def create_styles(size, fontsize,
        show_armeen=True, show_dorf=True, background=False):
    """erstellt ein passendes Stylesheet
    """

    text = '#karte tr td {'
    text += '    padding:0px;'
    text += '    height: ' + str(size) + 'px;'
    text += '    width: ' + str(size) + 'px;'
    text += '    background-repeat:no-repeat;'
    text += '    font-size: ' + str(fontsize) + 'pt;'
    text += '    text-align:center;'
    text += '}'
    text += 'div.armeen {'
    text += '    margin-left: ' + str(fontsize-5) + 'px;'
    if show_armeen and not show_dorf:
        text += '    margin-top:5px;'
    text += '    text-align:left;'
    text += '    max-height: ' + str(fontsize-5) + 'px;'
    text += '}'
    text += 'span.armee_dark {'
    text += '    display: inline-block;'
    if fontsize > 8:
        text += '    height: ' + str(fontsize-5) + 'px;'
        text += '    width: ' + str(fontsize-5) + 'px;'
        text += '    border: 1px solid white;'
    else:
        text += '    height: 0px;'
        text += '    width: 0px;'
    text += '}'
    text += 'span.armee_bright {'
    text += '    display: inline-block;'
    if fontsize > 8:
        text += '    height: ' + str(fontsize-5) + 'px;'
        text += '    width: ' + str(fontsize-5) + 'px;'
        text += '    border: 1px solid black;'
    else:
        text += '    height: 0px;'
        text += '    width: 0px;'
    text += '}'
    text += 'td.navi, div.navi{'
    if background:
        text += '    background-color:#333333;'
    text += '    font-weight:bold;'
    text += '    font-size:12pt;'
    text += '}'
    return text

def small_map(x, y, level="N", sicht=2):
    """Eine kleine integrierbare Karte

    vorher sollte L{create_styles<karte.create_styles>} abgesetzt werden

    @param x: Mittelpunkt X
    @type x: C{IntType}
    @param y: Mittelpunkt Y
    @type y: C{IntType}
    @param sicht: Sichtweite vom Mittelpunkt
    @type sicht: C{IntType}
    """

    from dorf import Dorf
    from armee import Armee
    from terrain import Terrain

    size = 32 
    fontsize = 9

    if level == "N" and config.allow_doerfer():
        dorf = Dorf()
        dorf.fetch_data()
        show_doerfer = True
    else:
        show_doerfer = False

    if config.allow_armeen():
        armee = Armee()
        armee.fetch_data(level)
        show_armeen = True
    else:
        show_armeen = False

    terrain = Terrain()
    terrain.fetch_data(level, x - sicht, x + sicht, y - sicht, y + sicht)

    width = size * (terrain.xmax - terrain.xmin + 1 + 2)
    karte = '\n\n<table id="karte" style="width:' + str(width) + 'px;">\n'
    karte += '<tr style="height:' + str(size) + 'px;"><td></td>\n'
    # X - Achse
    for x in range(terrain.xmin, terrain.xmax + 1):
        karte += '<td>' + str(x) + '</td>\n'
    for y in range(terrain.ymin, terrain.ymax + 1):
        karte += '<tr style="height:' + str(size) + 'px;">\n'
        karte += '<td>' + str(y)  + '</td>\n' # Y - Achse
        for x in range(terrain.xmin, terrain.xmax + 1):
            if terrain.has(x,y): # Kartenbereich
                terrain.get(x,y)
                row = '<td style="background-image:url(/img/terrain/'
                row += str(size) + '/' + terrain.entry["terrain"]
                row += '.gif);">'

                if (show_doerfer and dorf.has(x,y)
                        and dorf.get(x,y)["rittername"] != "."):
                    color = dorf.get(x,y)['allyfarbe']
                    row += __detail_link(x, y, level, color, new_window=False)
                elif show_armeen and armee.has(x,y):
                    color = None
                    row += __detail_link(x, y, level, color, new_window=False)

                if show_doerfer and dorf.has(x,y):
                    row += __dorf(dorf, x, y, terrain)
                if show_armeen:
                    row += __armeen(armee, x, y)

                row += '</a></td>\n'
                karte += row
            else:
                karte += '<td></td>\n'
        # y - Achse
        karte += '<td>' + str(y) + '</td></tr>\n'
    # X - Achse
    karte += '<tr style="height:' + str(size) + 'px;"><td></td>\n'
    for x in range(terrain.xmin, terrain.xmax + 1):
        karte += '<td>' + str(x) + '</td>\n'
    karte += '</table>\n'
    return karte


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
    print '<script src="' + ausgabe.prefix + '/show/javascript"',
    print 'type="text/javascript"></script>'
    print '</head>\n'
    print '<body>\n'

    if "list" in form:
        print '<h1>' + title + '</h1>'
        list_maps()
    else:
        # Zeige eine Karte


        # Bereite gewuenschte Layer und Bereiche vor
        if "level" in form:
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
        if not allow_dorf or "doerfer" not in layer:
            show_dorf = False
        else:
            show_dorf = True
            dorf = Dorf()
            if "neu" in layer:
                add_cond = "datediff(now(), aktdatum) < "+str(config.tage_neu)
                dorf.set_add_cond(add_cond)
            dorf.fetch_data()

        if allow_armeen and "armeen" in layer:
            show_armeen = True
            armee = Armee()
            if "alt" in layer:
                armee.replace_cond("TRUE") # keine Bedingung
            elif "neu" in layer:
                armee.set_add_cond("hour(timediff(now(), last_seen)) < 6")
            armee.fetch_data(level)
        else:
            show_armeen = False

        terrain = Terrain()
        if "x1" in form:
            if int(form["x2"].value) >= 999 and show_armeen:
                terrain.fetch_data(level, armee.xmin-15, armee.xmax+15,
                        armee.ymin-10, armee.ymax+10)
            else:
                terrain.fetch_data(level, form["x1"].value,form["x2"].value,
                        form["y1"].value, form["y2"].value)
        else:
            terrain.fetch_data(level)


        # Formatierungen
        background = int(form["x2"].value) >= 999
        print '<style type="text/css">'
        print create_styles(size, fontsize, show_armeen, show_dorf, background)
        print '</style>\n'

        # Detailboxen
        if config.is_kraehe() or config.is_tw():
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
        cross = int(form["x2"].value) < 999
        __print_navi(cross)

        # Schalter
        print '<div style="z-index:2; position:fixed;'
        print ' bottom:10px; right:20px;" class="navi">'
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
                    if show_dorf and not config.is_kraehe() and dorf.has(x,y):
                        row += '; color:'
                        row += dorf.get(x,y)['allyfarbe']
                    if "abgang" in terrain.entry:
                        row += '; border: 1px solid red'
                    if "aufgang" in terrain.entry:
                        row += '; border: 1px solid green'
                    if "quest" in terrain.entry:
                        row += '; border: 1px solid yellow'
                    row += ';"' # style attribut auf jeden Fall zumachen
                    if show_dorf and not config.is_kraehe() and dorf.has(x,y):
                        if util.brightness(dorf.get(x,y)['allyfarbe']) < 55:
                            row += ' class="dark"'
                        else:
                            row += ' class="bright"'

                    # Detail-Mouse-Over
                    if config.is_kraehe() or config.is_tw():
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
