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

function changeLink(layer, a) {
    // alte Layer finden
    var exp1 = "((armeen|doerfer|clean|neu)"
    var exp2 = "(\\+(armeen|doerfer|clean|neu))*)";
    var exp = new RegExp(exp1 + exp2);
    var match = a.href.match(exp);
    if (match) {
        var oldLayer = match[1].split("+");
    } else {
        var oldLayer = ["armeen", "doerfer"];
    }
    // neue Layer erstellen
    if (layer[0] == "+") {
        var newLayer = oldLayer;
        if (!inArray(layer.substr(1), newLayer)) {
            newLayer.push(layer.substr(1));
            newLayer = removeFrom("clean", newLayer);
        }
    } else { // -
        var newLayer = removeFrom(layer.substr(1), oldLayer);
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
            a.href = a.href.replace(exp, "");
        } else {
            a.href = a.href.replace(exp, newLayer.join("+"));
        }
    } else if (newLayer !== null) {
        exp = /(normal|small)/;
        match = a.href.match(exp);
        if (match) {
            exp = new RegExp("\\/" + exp.source);
            newEnd = newLayer.join("+") + '/' + match[0];
            a.href = a.href.replace(exp, newEnd);
        } else {
            a.href = a.href + '/' + newLayer.join("+");
        }
    }
}

function changeLinks(layer) {
    // passe Links an
    var tables = document.getElementsByTagName("table");
    for (var i=0; i < tables.length; i++) {
        if (tables[i].className == "navi") {
            var as = tables[i].getElementsByTagName("a");
            for (var j=0; j < as.length; j++) {
                changeLink(layer, as[j]);
            }
        }
    }
    var divs = document.getElementsByTagName("div");
    for (var i=0; i < divs.length; i++) {
        if (divs[i].className == "navi") {
            var as = divs[i].getElementsByTagName("a");
            for (var j=0; j < as.length; j++) {
                if (as[j].firstChild.data != "Index") {
                    changeLink(layer, as[j]);
                }
            }
        }
    }
}


function toggleArmeen() {
    var showArmies = document.getElementById("armeeschalter").checked;
    var armeeSpan = document.getElementById("armeeschalter")
        .nextSibling.nextSibling;
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
        armeeSpan.style.color = "green";
    } else {
        changeLinks("-armeen");
        armeeSpan.style.color = "";
    }
}

function toggleDorf() {
    var showDorf = document.getElementById("dorfschalter").checked;
    var dorfSpan = document.getElementById("dorfschalter")
        .nextSibling.nextSibling;
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
        dorfSpan.style.color = "green";
    } else {
        changeLinks("-doerfer");
        dorfSpan.style.color = "";
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
    // serverseitig escapen bringt hier nichts !
    str = str.replace(/</g, "&lt;")
    str = str.replace(/>/g, "&gt;")
    // damit ich doch nen BR setze kann, auch keine standard entitiy
    str = str.replace(/&br;/g, "<br />")
    /* Das ist keine Standard HTML-Entity
     * damit es wirklich nicht als "|" interpretiert wird
     */
    return str.replace(/&vbar;/g, "|")
}

function showPos(liste) {
    var descRow;
    var coordsOnly;
    if (liste.indexOf("|") == -1) {
        coordsOnly = true;
        descRow = '<div style="float:left; width:7em;">' + liste + '</div>';
    } else {
        coordsOnly = false;
        liste = liste.split("|");
        for (var i=0; i < liste.length; i++) {
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
    if (!coordsOnly && liste.length > 7) {
        descRow = '<table class="detail">';
        var numFields = parseInt(liste[7],10);
        var mid = Math.ceil(numFields/2);
        for (var i=8; i < liste.length; i+=numFields) {
            descRow += '<tr><td style="color:' + liste[i] + '">'
                    + liste[i+1] + '</td>';
            for (var j=i+2; j < (i + numFields); j++) {
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
