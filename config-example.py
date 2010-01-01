"""Konfiguration der DB und Berechtigungen"""

import re
import os

# Datenbank
db_host = "localhost"
db_user = ""
db_passwd = ""
db = ""

def is_kraehe(username):
    return not re.match("/tw", os.environ['SCRIPT_URL'])

def is_tw(username):
    return re.match("/tw", os.environ['SCRIPT_URL'])

# vim:set shiftwidth=4 expandtab smarttab:
