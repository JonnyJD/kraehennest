function showPos(liste) {
	var descRow;
	if (liste.indexOf("|") == -1) {
		descRow = '<div style="float:left; width:7em;">' +
			liste + '</div>';
	} else {
		liste = liste.split("|");
		descRow = '<div style="float:left; width:7em;">' +
			liste[0] + '</div>';
		descRow += '<div style="float:left; width:15em;">' +
			liste[1] + '</div>';
		descRow += '<div style="float:left; width:15em;">' +
			liste[2] + '</div>';
		descRow += '<div style="float:left; width:15em;">' +
			liste[3] + '</div>';
		descRow += '<div style="float:left; width:5em;">' +
			liste[4] + '</div>';
		var mauer;
		switch(liste[5]) {
			case "o": mauer = "ohne Mauer"; break;
			case "k": mauer = "kleine Mauer"; break;
			case "m": mauer = "mittlere Mauer"; break;
			case "g": mauer = "gro&szlig;e Mauer"; break;
			case "u": mauer = "un&uuml;berwindbare Mauer"; break;
			default: mauer = "Mauer unbekannt";
		}
		descRow += '<div style="float:left; width:15em;">' +
			mauer + '</div>';
		descRow += '<div style="float:left; width:10em;">' +
			liste[6] + '</div>';

	}
	document.getElementById("dorfdetail").innerHTML = descRow;
	if (liste.length > 7) {
		descRow = '<table class="detail">';
		for (i=7; i < liste.length; i+=4) {
			descRow += '<tr><td style="text-align:left;' +
			       	' color:' + liste[i] + '">' +
				liste[i+1] + '</td><td>' + liste[i+2] +
				'</td><td>' + liste[i+3] + '</td></tr>';
		}
		descRow += '</table>';
		document.getElementById("armeedetail").innerHTML = descRow;
	}
}
function delPos() {
	document.getElementById("dorfdetail").innerHTML = "<div>&nbsp;</div>";
	document.getElementById("armeedetail").innerHTML = "<div>&nbsp;</div>";
}
