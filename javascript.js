function inArray(text, arr) {
    if (arr === null) {
        return false;
    } else {
        for (var i=0; i < arr.length; i++) {
            if (arr[i] == text) {
                return true;
            }
        }
    }
}

function removeFrom(text, arr) {
    if (arr !== null) {
        for (var i=0; i < arr.length; i++) {
            if (arr[i] == text) {
                arr.splice(i, 1);
            }
        }
    }
    return arr
}

function changeLinks(layer) {
    // passe Links an
    var warn = false;
    var tables = document.getElementsByTagName("table");
    for (var i=0; i < tables.length; i++) {
        if (tables[i].className="navi") {
            as = tables[i].getElementsByTagName("a");
            for (var j=0; j < as.length; j++) {
                // alte Layer finden
                exp1 = "((armeen|doerfer|clean|neu)"
                exp2 = "(\\+(armeen|doerfer|clean|neu))*)";
                exp = new RegExp(exp1 + exp2);
                match = as[j].href.match(exp);
                if (match) {
                    oldLayer = match[1].split("+");
                } else {
                    oldLayer = ["armeen", "doerfer"];
                }
                // neue Layer erstellen
                if (layer[0] == "+") {
                    newLayer = oldLayer;
                    if (!inArray(layer.substr(1), newLayer)) {
                        newLayer.push(layer.substr(1));
                        newLayer = removeFrom("clean", newLayer);
                    }
                } else { // -
                    newLayer = removeFrom(layer.substr(1), oldLayer);
                    if (newLayer.length == 0) {
                        newLayer = ["clean"];
                    }
                }
                // Standardwerte
                if (newLayer && newLayer.sort().join("+") == "armeen+doerfer") {
                    newLayer = null;
                }
                // neuen Layer setzen
                if (match) {
                    if (newLayer === null) {
                        exp = new RegExp("\\/" + exp.source);
                        as[j].href = as[j].href.replace(exp, "");
                    } else {
                        as[j].href = as[j].href.replace(exp,newLayer.join("+"));
                    }
                } else if (newLayer !== null) {
                    exp = /(normal|small)/;
                    match = as[j].href.match(exp);
                    if (match) {
                        exp = new RegExp("\\/" + exp.source);
                        newEnd = newLayer.join("+") + '/' + match[0];
                        as[j].href = as[j].href.replace(exp, newEnd);
                    } else {
                        as[j].href = as[j].href + '/' + newLayer.join("+");
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
