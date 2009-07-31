# schreibt die url.conf so um
# dass das auch mit den Rechten auf kraehen.org klappt
# die urspruengliche url.conf wird nicht geaendert,
# damit sie auf Testserver laeuft

CGI=/usr/lib/cgi-bin
ROOT=/var/www/kraehen.org
NEST=$(ROOT)/nest
KARTE=$(ROOT)/karte

serverconf:
	echo -e "\
	# Diese Datei wird mit 'make serverconf' automatisch erstellt\n\
	# bitte NICHT manuell editieren!" > serverurl.conf
	cat url.conf \
	| sed \
	-e '1,4d' \
	-e 's:karte/datenpflege:kartedatenpflege:' \
	-e 's:\(\w*\)/cgi-bin/\(.*\)\w*\[PT\]:\1$(CGI)/\2:' \
	-e 's:\(\w*\)/nest/\(.*\)\w*\[PT\]:\1$(NEST)/\2:' \
	-e 's:\(\w*\)/karte/\(.*\)\w*\[PT\]:\1$(KARTE)/\2:' \
	-e 's:kartedatenpflege:karte/datenpflege:' \
	>> serverurl.conf

clean:
	rm serverurl.conf
