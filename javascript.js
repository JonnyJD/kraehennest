function showPos(liste) {
	var descRow;
	if (liste.indexOf("|") == -1) {
		descRow = '<div style="float:left; width:7em;">'+liste+'</div>';
	} else {
		liste = liste.split("|");
		descRow = '<div style="float:left; width:7em;">'+liste[0]+'</div>';
		descRow += '<div style="float:left; width:15em;">'+liste[1]+'</div>';
		descRow += '<div style="float:left; width:15em;">'+liste[2]+'</div>';
		descRow += '<div style="float:left; width:15em;">'+liste[3]+'</div>';
		descRow += '<div style="float:left; width:5em;">'+liste[4]+'</div>';
		var mauer;
		switch(liste[5]) {
			case "o": mauer = "ohne Mauer"; break;
			case "k": mauer = "kleine Mauer"; break;
			case "m": mauer = "mittlere Mauer"; break;
			case "g": mauer = "gro&szlig;e Mauer"; break;
			case "u": mauer = "un&uuml;berwindbare Mauer"; break;
			default: mauer = "Mauer unbekannt";
		}
		descRow += '<div style="float:left; width:15em;">'+mauer+'</div>';
		descRow += '<div style="float:left; width:10em;">'+liste[6]+'</div>';
	}
	document.getElementById("position").innerHTML = descRow;
}
function delPos() {
	document.getElementById("position").innerHTML = "<div>&nbsp;</div>";
}
