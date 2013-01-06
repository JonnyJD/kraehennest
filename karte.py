#!/usr/bin/env python
"""Skript um die Karte anzuzeigen und eine Kartenuebersicht zu generieren"""

import config

if config.debug:
    import cgitb
    cgitb.enable()

import cgi
import os
from textwrap import dedent

import ausgabe
import util
from model.terrain import Terrain
from model.armee import Armee
from model.dorf import Dorf
from view import format, common_terrain
from view.karte import escape
from view.karte import small_map, create_styles, nav_link, detail_link
from view.karte import dorf_output, armee_output


many_armeen_limit = 8
"""Gibt an ab welcher Armeezahl auf einem Feld weniger Infos gezeigt werden"""

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


def __mouseover(x, y, typ, dorf, armeen):
    """creates the mouseover/mouseout for the map cells
    """

    details = []
    # coordinates and terrain type
    if is_kraehe and terrain.entry["typ"]:
        details.append("%d,%d %s" % (x, y, "." * terrain.entry["typ"]))
    else:
        details.append("%d,%d" % (x, y))

    # Dorf
    if dorf:
        cols = ['rittername', 'alliname', 'dorfname', 'dorflevel',
                'mauer', 'aktdatum']
        details.extend(map(format, [dorf[col] for col in cols]))
    elif armeen:
        # fill up to the armee part
        details.extend(["?" for i in range(6)])

    # Armeen
    if armeen:
        # Less infos per armee if there are many armeen
        if len(armeen) < many_armeen_limit:
            many_armeen = False
            details.append('7')
        else:
            many_armeen = True
            details.append('4')
        # Armeen anhaengen
        for armee in armeen:
            details.append(escape(armee["allyfarbe"]))
            if armee["rittername"] == "Keiner" and many_armeen:
                armee_str = escape(armee["name"])
            else:
                armee_str = escape(armee["rittername"])
            if armee["schiffstyp"] is not None and many_armeen:
                armee_str += '&br;[%s]' % escape(armee["schiffstyp"])
            details.append(armee_str) # name (and possibly schiffstyp)
            details.append(format(armee["size"]))
            details.append(format(armee["strength"]))
            if not many_armeen:
                if armee["schiffstyp"] is None:
                    details.append(escape(armee["name"]))
                else:
                    details.append('%s&br;[%s]'
                        % (escape(armee["name"]), escape(armee["schiffstyp"])))
                details.append(format(armee["ap"]))
                details.append(format(armee["bp"]))
    return ' onmouseover="showPos(\'%s\')" onmouseout="delPos()"' % (
                                                        "|".join(details))

# Aufruf direkt: Karten anzeigen
# mod_python.cgihandler doesn't count as direct
#if __name__ == '__main__':
if True:
    form = cgi.FieldStorage()

    if "list" in form:  title = "Kr&auml;henkarten"
    else:               title = "Kr&auml;henkarte"

    if "HTTP_IF_MODIFIED_SINCE" in os.environ:
        cache_string = os.environ["HTTP_IF_MODIFIED_SINCE"]
        db_string = util.map_last_modified_http(
                config.allow_doerfer(message=False),
                config.allow_armeen(message=False))
        if db_string == cache_string:   is_still_valid = True
        else:                           is_still_valid = False
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
        # http header
        print 'Cache-Control: no-cache,must-revalidate'
        print 'Content-type: text/html; charset=utf-8\n'
        html_head = """\
        <!DOCTYPE html>
        <html><head>
        <title>%s</title>
        <meta name="robots" content="noindex, nofollow">
        <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        <link rel="stylesheet" type="text/css" href="%s/show/stylesheet">
        <script src="%s/show/javascript" type="text/javascript"></script>
        </head>\n""" % (title, ausgabe.prefix, ausgabe.prefix)
        print dedent(html_head)
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
                print '<div id="dorfdetail"><div>&nbsp;</div></div>'
                print '<br /><div></div>'
                if show_armeen:
                    # Armeedetail
                    print '<div id="armeedetail"><div>&nbsp;</div></div>'

            # Kartennavigation
            cross = int(form["x2"].value) < 999
            __print_navi(cross)

            # Schalter
            print '<div style="z-index:2; position:fixed;'
            print ' bottom:10px; right:20px;" class="navi">'
            # Soft-Reload
            print "<a href=\"%s\">Soft-Reload</a><br />\n<br />" % (
                                        os.environ["SCRIPT_URL"])
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
            strings = []
            strings.append('\n\n<table id="karte" style="width:%dpx;">' % width)
            strings.append('<tr style="height:%dpx;"><td></td>' % size)
            # X - Achse
            for x in range(terrain.xmin, terrain.xmax + 1):
                strings.append('<td>%d</td>' % x)
            for y in range(terrain.ymin, terrain.ymax + 1):
                # Y - Achse
                strings.append('<tr style="height:%dpx;"><td>%d</td>'
                        % (size, y))
                for x in range(terrain.xmin, terrain.xmax + 1):
                    if terrain.has(x,y): # Kartenbereich

                        # Terrainhintergrund
                        terrain.get(x,y)
                        styles = []
                        classes = []
                        strings.append('<td')
                        if terrain.entry["terrain"] in common_terrain:
                            classes.append('t%s' % terrain.entry["terrain"])
                        else:
                            styles.append(
                                'background-image:url(/img/terrain/%d/%s.gif);'
                                % (size, terrain.entry["terrain"]))
                        if show_armeen and not show_dorf:
                            styles.append('vertical-align:top')
                        if show_dorf and not is_kraehe and dorf.has(x,y):
                            styles.append('color:%s'
                                    % format(dorf.get(x,y)['allyfarbe']))
                        if "abgang" in terrain.entry:
                            styles.append('border: 1px solid red')
                        if "aufgang" in terrain.entry:
                            styles.append('border: 1px solid green')
                        if "quest" in terrain.entry:
                            styles.append('border: 1px solid yellow')
                        if allow_target and "ziel" in terrain.entry:
                            styles.append('border: 1px solid blue')
                        if show_dorf and not is_kraehe and dorf.has(x,y):
                            if util.brightness(dorf.get(x,y)['allyfarbe']) < 55:
                                classes.append('dark')
                            else:
                                classes.append('bright')
                        # add complete styles and classes
                        if len(classes) > 0:
                            strings.append(' class="%s"' % " ".join(classes))
                        if len(styles) > 0:
                            strings.append(' style="%s"' % "; ".join(styles))

                        # Detail-Mouse-Over
                        if allow_details:
                            # current dorf
                            if show_dorf:       this_dorf = dorf.get(x, y)
                            else:               this_dorf = None
                            # current armee
                            if show_armeen:     these_armeen = armee.get(x, y)
                            else:               these_armeen = None
                            # current terrain type
                            if is_kraehe:       this_typ = terrain.entry["typ"]
                            else:               this_typ = None
                            # build onmouseover and onmouseout
                            strings.append(__mouseover(
                                x, y, this_typ, this_dorf, these_armeen))

                        strings.append('>')     # close starting td

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
                            strings.append(detail_link(x, y, level, color))

                        # Dorf
                        if show_dorf and dorf.has(x,y):
                            strings.append(dorf_output(dorf, x, y, terrain))

                        # Armeen
                        if show_armeen:
                            strings.append(armee_output(armee, x, y))
                        if show_detail_link:
                            strings.append('</a>')
                        strings.append('</td>\n')
                    else: # not terrain.has(x,y):
                        strings.append('<td></td>')
                # y - Achse
                strings.append('<td>%d</td></tr>\n' % y)
            # X - Achse
            strings.append('<tr style="height:%dpx;"><td></td>' % size)
            for x in range(terrain.xmin, terrain.xmax + 1):
                strings.append('<td>%d</td>' % x)
            strings.append('</table>')
            print "".join(strings)

        print "\n</body></html>"

# vim:set shiftwidth=4 expandtab smarttab:
