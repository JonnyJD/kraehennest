# Das Skript schreibt die url.conf so um
# dass das auch mit den Rechten auf kraehen.org klappt.
# Der Knackpunkt ist, dass die TW oder Externe
# nicht am Ende doch ein Kraehenpasswort abgefragt bekommen.
# Die urspruengliche url.conf wird nicht geaendert,
# damit sie auf Testserver laeuft.

CGI=/usr/lib/cgi-bin
ROOT=/var/www/kraehen.org
NEST=$(ROOT)/nest
KARTE=$(ROOT)/karte

export QUERY_STRING:=group&x1=0&x2=998&y1=0&y2=998
export SCRIPT_URL:=/show/karte

compile: normal serverconf
	python -m compileall -l .

normal:
	sed -i '1s/python2/python/' index.py dispatch.py
	sed -i '1s/python2/python/' karte.py admin.py
	sed -i '1s/python2/python/' allianz.py armee.py dorf.py reich.py
	sed -i '1s/python2/python/' feld.py

arch:
	sed -i '1s/python$$/python2/' index.py dispatch.py
	sed -i '1s/python$$/python2/' karte.py admin.py
	sed -i '1s/python$$/python2/' allianz.py armee.py dorf.py reich.py
	sed -i '1s/python$$/python2/' feld.py
	python2 -m compileall -l -q .

serverconf:
	echo -e "\
	# Diese Datei wird mit 'make serverconf' automatisch erstellt\n\
	# bitte NICHT manuell editieren!" > serverurl.conf
	cat url.conf \
	| sed \
	-e '1,4d' \
	-e 's:\(\w*\)/cgi-bin/\(.*\)\w*\[PT\]:\1$(CGI)/\2:' \
	-e 's:\(\w*\)/nest/\(.*\)\w*\[PT\]:\1$(NEST)/\2:' \
	-e 's:\(\w*\)/karte/\(.*\)\w*\[PT\]:\1$(KARTE)/\2:' \
	>> serverurl.conf

doc:
	epydoc -v --output=/var/www/doc.kraehen.org/tools/nest \
		--show-imports --inheritance=grouped \
		--name=Kraehenauge --exclude=config *.py

doctest:
	epydoc --check -v --simple-term \
		--exclude=config *.py \
		| grep -v __package__

clean: normal
	rm -f serverurl.conf test.xml
	rm -f *.pyc
	rm -rf __pycache__

test: test-karte

test-xml:
	cp /srv/http/cgi-bin/saves/127.0.0.1_xml test.xml
	python2 test.py \
	| sed -e 's: /home.*/trunk/: :'

test-karte:
	#python2 -m cProfile -o profile karte.py > /dev/null
	python2 -m cProfile -o profile karte.py
	python2 -c "import pstats; pstats.Stats('profile').sort_stats('cum').print_stats('\A[a-z]*.py', 10)"
	python2 -c "import pstats; pstats.Stats('profile').sort_stats('time').print_stats('\A[a-z]*.py', 10)"
