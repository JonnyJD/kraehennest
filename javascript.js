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
                if (parseInt(liste[j],10)) {
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
    document.getElementById("dorfdetail").innerHTML = "<div>&nbsp;</div>";
    document.getElementById("armeedetail").innerHTML = "<div>&nbsp;</div>";
}

/* vim:set shiftwidth=4 expandtab smarttab: */
