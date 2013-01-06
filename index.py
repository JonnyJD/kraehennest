#!/usr/bin/env python
"""Das ist die Indexseite mit Links zu Uebersichten."""

import config

if config.debug:
    import cgitb
    cgitb.enable()

from datetime import datetime, timedelta
import cgi
from user import User
import ausgabe


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


# Aufruf als Skript
# mod_python.cgihandler doesn't count as direct
#if __name__ == "__main__":
if True:
    try:
        user = User()
        if user.last_seen_auge:
            delta = datetime.now() - user.last_seen_auge
        else:
            delta = timedelta(weeks=9999)

        styles = "#augenzeit {"
        styles += "    font-weight:bold;"
        if delta > timedelta(hours=48):
            styles += "    color:red;"
        styles += "}"
        ausgabe.print_header("Kr&auml;hennest",styles)

        augenstring = ausgabe.datetime_delta_string(user.last_seen_auge)
        print '<p>Der eingeloggte Benutzer <strong>' + user.name + '</strong>',
        print 'hat zuletzt <span id="augenzeit">' + augenstring + '</span>',
        print 'das Kr&auml;henauge benutzt.</p>'
    except KeyError, e:
        user = None
        ausgabe.print_header("Kr&auml;hennest")


    # Uebersichtsseiten
    if config.is_kraehe():
        print '<div class="box">'
        print '<h2>&Uuml;bersichtsseiten</h2>'
        print ausgabe.link("/show/allianzen", "Allianzen")
        print ausgabe.link("/show/reiche", "Reiche", br=True)
        print ausgabe.link("/show/doerfer", "D&ouml;rfer", br=True)
        print ausgabe.link("/show/armeen", "Armeen", br=True)
        print '</div>'
    # Direktlinks
    if config.is_kraehe():
        print '<div class="box">'
        print '<h2>Direktlinks</h2>'
        print ausgabe.link("/show/allianz/60", "Kr&auml;hen")
        if user and user.r_id:
            url = "/show/reich/" + str(user.r_id)
            rittername = cgi.escape(user.rittername)
            print ausgabe.link(url, rittername, br=True)
        print ausgabe.link("/show/reich/174", "Keiner", br=True)
        print ausgabe.link("/show/reich/113", "Plunkett", br=True)
        print '</div>'
    # Adminbereich
    print '<div class="box">'
    print '<h2>Administration</h2>'
    if config.is_admin():
        if config.is_kraehe():
            print '<a href="/karte/datenpflege.php">Datenpflege</a>'
            print ausgabe.link("/show/versionen", "Versionsliste", br=True)
            print ausgabe.link("/delete", "L&ouml;schliste", br=True)
        else:
            print ausgabe.link("/show/versionen", "Versionsliste")
    print '<br /><a href="/create_md5.html">Account erstellen</a>'
    if ausgabe.prefix:
        if ausgabe.prefix == "/ext":
            suffix = "extern"
	else:
            suffix = ausgabe.prefix[1:]
	auge = "/kraehenauge_" + suffix + ".user.js"
    	print ausgabe.link(auge, "Kr&auml;henauge", br=True)
    else:
        auge = "/auge/kraehenauge.user.js"
    	print ausgabe.link(auge, "Kr&auml;henauge", br=True)
    print '</div>'

    list_maps()

    ausgabe.print_footer()

# vim:set shiftwidth=4 expandtab smarttab:
