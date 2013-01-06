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
