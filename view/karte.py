#!/usr/bin/env python
"""Modul um die Karte anzuzeigen und eine Kartenuebersicht zu generieren"""

from types import StringType

import config
import ausgabe
import util
from model.terrain import Terrain
from model.armee import Armee
from model.dorf import Dorf


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

def dorf_output(dorf, x, y, terrain=None):
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

def armee_output(armee, x, y):
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
            text += format(entry["allyfarbe"]) + ';"></span>'
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
