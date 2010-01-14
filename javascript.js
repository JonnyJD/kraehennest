function changeLinks(layer) {
    // passe Links an
    var warn = false;
    var tables = document.getElementsByTagName("table");
    for (var i=0; i < tables.length; i++) {
        if (tables[i].className="navi") {
            var as = tables[i].getElementsByTagName("a");
            for (var j=0; j < as.length; j++) {
                // alten Layer finden
                var match = as[j].href.match(/(armeen|doerfer|clean)/);
                if (match) {
                    var oldLayer = match[0];
                } else {
                    var oldLayer = null; // also beides
                }
                // neuen Layer finden
                if (layer[0] == "+") {
                    if (oldLayer == "clean") {
                        newLayer = layer.substr(1);
                    } else {
                        newLayer = null;
                    }
                } else { // -
                    if (oldLayer == null) {
                        if (layer == "-armeen") {
                            newLayer = "doerfer";
                        } else {
                            newLayer = "armeen";
                        }
                    } else {
                        newLayer = "clean";
                    }
                }
                // neuen Layer setzen
                if (match) {
                    if (newLayer === null) {
                        exp = /\/(armeen|doerfer|clean)/
                        as[j].href = as[j].href.replace(exp, "");
                    } else {
                        exp = /(armeen|doerfer|clean)/
                        as[j].href = as[j].href.replace(exp, newLayer);
                    }
                } else if (newLayer !== null) {
                    match = as[j].href.match(/(normal|small)/);
                    if (match) {
                        exp = /(normal|small)/
                        newEnd = newLayer + '/' + match[0];
                        as[j].href = as[j].href.replace(exp, newEnd);
                    } else {
                        as[j].href = as[j].href + '/' + newLayer;
                    }
                }
            }
        }
    }
}

function toggleArmeen() {
    var showArmies = document.getElementById("armeeschalter").checked;
    var divs = document.getElementsByTagName("div");
    for (var i=0; i < divs.length; i++) {
        if (divs[i].className == "armeen") {
            if (showArmies) {
                divs[i].style.display = "block";
            } else {
                divs[i].style.display = "none";
            }
        }
    }
    if (showArmies) {
        changeLinks("+armeen");
    } else {
        changeLinks("-armeen");
    }
}

function toggleDorf() {
    var showDorf = document.getElementById("dorfschalter").checked;
    var divs = document.getElementsByTagName("div");
    for (var i=0; i < divs.length; i++) {
        if (divs[i].className == "dorf") {
            if (showDorf) {
                divs[i].style.display = "block";
            } else {
                divs[i].style.display = "none";
            }
        }
    }
    if (showDorf) {
        changeLinks("+doerfer");
    } else {
        changeLinks("-doerfer");
    }

    // kleinere Stilaenderungen
    var tds = document.getElementById("karte").getElementsByTagName("td");
    for (var i=0; i < tds.length; i++) {
        if (tds[i].style.backgroundImage) {
            if (showDorf) {
                tds[i].style.verticalAlign = "";
            } else {
                tds[i].style.verticalAlign = "top";
            }
        }
    }
    var divs = document.getElementsByTagName("div");
    for (var i=0; i < divs.length; i++) {
        if (divs[i].className == "armeen") {
            if (showDorf) {
                divs[i].style.marginTop = "";
            } else {
                divs[i].style.marginTop = "5px";
            }
        }
    }
}

function my_unescape(str) {
    /* Das ist keine Standard HTML-Entity
     * damit es wirklich nicht als "|" interpretiert wird
     */
    return str.replace(/&vbar;/g, "|")
}

function showPos(liste) {
    var descRow;
    if (liste.indexOf("|") == -1) {
        descRow = '<div style="float:left; width:7em;">' + liste + '</div>';
    } else {
        liste = liste.split("|");
        for (i=0; i < liste.length; i++) {
            liste[i] = my_unescape(liste[i])
        }
        descRow = '<div style="float:left; width:7em;">'  + liste[0] + '</div>';
        descRow += '<div style="float:left; width:15em;">'+ liste[1] + '</div>';
        descRow += '<div style="float:left; width:15em;">'+ liste[2] + '</div>';
        descRow += '<div style="float:left; width:15em;">'+ liste[3] + '</div>';
        descRow += '<div style="float:left; width:5em;">' + liste[4] + '</div>';
        var mauer;
        switch(liste[5]) {
            case "o": mauer = "ohne Mauer"; break;
            case "k": mauer = "kleine Mauer"; break;
            case "m": mauer = "mittlere Mauer"; break;
            case "g": mauer = "gro&szlig;e Mauer"; break;
            case "u": mauer = "un&uuml;berwindbare Mauer"; break;
            default: mauer = "Mauer unbekannt";
        }
        descRow += '<div style="float:left; width:15em;">' + mauer + '</div>';
        descRow += '<div style="float:left; width:10em;">'+ liste[6] + '</div>';
    }
    document.getElementById("dorfdetail").innerHTML = descRow;
    if (liste.length > 7) {
        descRow = '<table class="detail">';
        numFields = parseInt(liste[7],10);
        mid = Math.ceil(numFields/2);
        for (i=8; i < liste.length; i+=numFields) {
            descRow += '<tr><td style="color:' + liste[i] + '">'
                    + liste[i+1] + '</td>';
            for (j=i+2; j < (i + numFields); j++) {
                if (numFields > 5 && (j-8) % numFields == mid) {
                    descRow += '</tr><tr>'
                }
                if (!isNaN(parseInt(liste[j],10)) || liste[j] == "?") {
                    descRow += '<td style="text-align:right">'
                            + liste[j] + '</td>';
                } else {
                    descRow += '<td>' + liste[j] + '</td>';
                }
            }
            descRow += '</tr>';
        }
        descRow += '</table>';
        document.getElementById("armeedetail").innerHTML = descRow;
    }
}

function delPos() {
    if (document.getElementById("dorfdetail")) {
        document.getElementById("dorfdetail").innerHTML = "<div>&nbsp;</div>";
    }
    if (document.getElementById("armeedetail")) {
        document.getElementById("armeedetail").innerHTML = "<div>&nbsp;</div>";
    }
}

/* vim:set shiftwidth=4 expandtab smarttab: */
