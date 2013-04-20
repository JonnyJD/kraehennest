#!/usr/bin/env python
"""Modul um die Karte anzuzeigen und eine Kartenuebersicht zu generieren"""

from textwrap import dedent
from types import StringType

import config
import ausgabe
import util
from model.terrain import Terrain
from model.armee import Armee
from model.dorf import Dorf


common_terrain = ["51", "11", "21", "6", "73", "71", "26", "28", "13", "101",
                  "64", "33", "73v1", "78", "41", "1", "52v4", "52", "79", "88"]

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

def center_link(x, y, level="N", text="zur Karte"):
    """Erstellt einen Kartenlink fuer eine Koordinate

    @return: HTML-Link
    @rtype: C{StringType}
    """
    layer = ["armeen", "doerfer"] # + center spaeter
    return nav_link(x, y, x, y, level, text, "center", 0, layer)

def escape(var):
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

def format(var):
    """Formatierte Ausgabe einer Variable

    @param var: Eingabevariable
    @return: C{"?"} bei None, sonst C{str(var)}
    @rtype: C{StringType}
    """
    if var == None:
        return "?"
    else:
        return escape(str(var))

def detail_link(x, y, level="N", color=None, new_window=True):
    """Startet den Detaillink.

    Nicht vergessen den Link wieder zu schliessen!

    @return: Start-Tag eines HTML-links
    @rtype: C{StringType}
    """
    strings = []
    strings.append('<a href="%s/show/feld/%d.%d' % (ausgabe.prefix, x, y))
    if level != "N":
        strings.append('/%s' % level )
    strings.append('"')
    if color is not None:
        strings.append(' style="color:%s' % color)
        if util.brightness(color) < 55:
            strings.append(';" class="dark"')
        else:
            strings.append(';" class="bright"')
    if new_window:
        strings.append(' target="_blank">')
    else:
        strings.append('>')
    return "".join(strings)

def dorf_output(dorf, x, y, terrain=None):
    """Kartenanzeige eines Dorfes
    
    @return: Dorf-DIV (HTML)
    @rtype: C{StringType}
    """

    dorf.get(x,y)
    strings = []
    strings.append('<div class="dorf">')
    if dorf.entry['rittername'] != ".":
        # translate(None, "<>"),  None erst ab python 2.6
        strings.append(
            dorf.entry['rittername'].replace("<", "").replace(">", "")[0:3])
    elif terrain is not None and config.is_kraehe() and terrain.entry["typ"]:
        strings.append("." * terrain.entry["typ"])
    elif config.is_kraehe():
        strings.append("_")
    else:
        strings.append(".")
    strings.append('</div>')
    return "".join(strings)

def armee_output(armee, x, y):
    """Kartenanzeige von Armeen auf einem Feld

    @return: Armee-DIV (HTML)
    @rtype: C{StringType}
    """

    strings = []
    if armee.has(x,y):
        strings.append('<div class="armeen">')
        for entry in armee.get(x,y):
            if util.brightness(entry["allyfarbe"]) < 55:
                strings.append('<span class="armee_dark"')
            else:
                strings.append('<span class="armee_bright"')
            strings.append(' style="background-color:%s;"></span>'
                    % format(entry["allyfarbe"]))
        strings.append('</div>')
    return "".join(strings)

def create_styles(size, fontsize,
        show_armeen=True, show_dorf=True, background=False):
    """erstellt ein passendes Stylesheet
    """

    strings = []
    karte = """\
    #karte tr td {
        -moz-box-sizing: border-box; /* height/width include border */
        padding: 0px;
        height: %dpx;
        width: %dpx;
        background-repeat: no-repeat;
        font-size: %dpt;
        text-align: center;
    }\n""" % (size, size, fontsize)
    strings.append(dedent(karte))

    for t in common_terrain:
        strings.append('#karte tr td.t%s { ' % t)
        strings.append('background-image:url(/img/terrain/%d/%s.gif); }\n' % (
                                                                    size, t))
    text = ""
    text += "".join(strings)
    text += 'div.armeen {\n'
    text += '    margin-left: ' + str(fontsize-5) + 'px;\n'
    text += '    font-size: 0pt;\n'
    if show_armeen and not show_dorf:
        text += '    margin-top: 5px;\n'
    text += '    text-align: left;\n'
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
        text += '    background-color: #333333;\n'
    text += '    font-weight: bold;\n'
    text += '    font-size: 12pt;\n'
    text += '}\n'
    return text


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
    if config.allow_hoehlen():
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
        } else if (document.URL.indexOf("p/show") != -1) {
            var link = "/p/show/karte/";
        } else if (document.URL.indexOf("dr/show") != -1) {
            var link = "/dr/show/karte/";
        } else {
            var link = "/show/karte/";
        }
        link += form.x1.value + "." + form.y1.value + "-";
        link += form.x2.value + "." + form.y2.value;
        level = "N";
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
        } else {
            link += "/clean";
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
    if (config.is_kraehe() or config.is_tw()
            or config.is_dr() or config.is_p()):
        print '<br />'
        print_area_link("osten", [1,2,3,4], "Der Osten", br=True)
        print_area_link("westen", [1,2,3],  "Der Westen", br=True)
        print_area_link("sueden", [1,2,3],  "Der S&uuml;den", br=True)
        print '<br />'
        print_area_link("drache", [1,2],    "Drachenh&ouml;hle", br=True)
        print "(Piraten)"
        print_area_link("axt", [1,2,3],     "Axtw&auml;chterquest", br=True)
        print "(Zentral)"
        print_area_link("schuetzen", [1],  "Meistersch&uuml;tzenquest", br=True)
        print "(K&uuml;ste)"
        print '<br />'
    if allow_armeen:
        print_link("/doerfer", "komplette Dorfkarte", br=True)
    print_area_link("", [1,2,3,4], "komplett", br=True)
    if allow_armeen:
        print "(cut)"
        print_link("/armeen", "reine Armeekarte", br=True)
        print "(cut)"
    print_link("/clean", "Terrainkarte", br=True)
    if config.allow_hoehlen():
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
<input name="y1" type="text" size="3" maxlength="3" value="280">
&nbsp;&nbsp; - &nbsp;&nbsp;
<input name="x2" type="text" size="3" maxlength="3" value="289">,
<input name="y2" type="text" size="3" maxlength="3" value="303">
"""
    elif config.is_tw():
      print \
"""
<input name="x1" type="text" size="3" maxlength="3" value="261">,
<input name="y1" type="text" size="3" maxlength="3" value="287">
&nbsp;&nbsp; - &nbsp;&nbsp;
<input name="x2" type="text" size="3" maxlength="3" value="292">,
<input name="y2" type="text" size="3" maxlength="3" value="322">
"""
    else:
      print \
"""
<input name="x1" type="text" size="3" maxlength="3" value="237">,
<input name="y1" type="text" size="3" maxlength="3" value="293">
&nbsp;&nbsp; - &nbsp;&nbsp;
<input name="x2" type="text" size="3" maxlength="3" value="271">,
<input name="y2" type="text" size="3" maxlength="3" value="323">
"""
    print """
</td></tr>
"""
    if config.allow_hoehlen():
        print """
<tr><td>Level:&nbsp;</td><td colspan="2">
<input name="level" type="radio" value="N" checked>N
<input name="level" type="radio" value="u1">U1
<input name="level" type="radio" value="u2">U2
<input name="level" type="radio" value="u3">U3
<input name="level" type="radio" value="u4">U4
</td></tr>
"""
    else:
        print """
<tr><td colspan="3">
<input name="level" type="hidden" value="N">
</td></tr>
"""
    print """
<tr><td style="vertical-align:top;">Layer:&nbsp;</td><td>
"""
    if allow_armeen:
        print '<input name="layer" value="armeen" type="checkbox" checked>',
        print 'Armeen<br />'
    print \
"""
<input name="layer" value="doerfer" type="checkbox" checked> D&ouml;rfer
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
    elif config.is_tw():
        print ausgabe.link("/show/karte/261.287-292.322")
    else:
        print ausgabe.link("/show/karte/237.293-271.323")
    print '</div>'
    print '</div>'


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

    terrain = Terrain()
    terrain.fetch_data(level, xmin, xmax, ymin, ymax)

    if imported:
        achsen = False
        new_window = True
    else:
        achsen = True
        new_window = False

    if config.allow_armeen(message=False):
        armee = Armee()
        armee.fetch_data(level, xmin, xmax, ymin, ymax)
        show_armeen = True
    else:
        show_armeen = False

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

                has_detail_link = False
                if config.is_kraehe():
                    if (show_doerfer and dorf.has(x,y)
                            and dorf.get(x,y)["rittername"] != "."):
                        row += detail_link(x, y, level, color, new_window)
                        has_detail_link = True
                    elif show_armeen and armee.has(x,y):
                        row += detail_link(x, y, level, color, new_window)
                        has_detail_link = True

                if show_doerfer and dorf.has(x,y):
                    row += dorf_output(dorf, x, y, terrain)
                if show_armeen:
                    row += armee_output(armee, x, y)

                if has_detail_link: row += '</a>'
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


# vim:set shiftwidth=4 expandtab smarttab:
