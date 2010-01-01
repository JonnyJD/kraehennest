"""Konfiguration der DB und Berechtigungen"""

import re
import os

# Datenbank
db_host = "localhost"
db_user = ""
db_passwd = ""
db = ""

def get_username():
    if 'REMOTE_USER' in os.environ:
        return os.environ['REMOTE_USER']
    else:
        return ""

def is_admin(username=None):
    return False

def is_kraehe(username=None):
    return not re.match("/tw", os.environ['SCRIPT_URL'])

def is_tw(username=None):
    return re.match("/tw", os.environ['SCRIPT_URL'])

# vim:set shiftwidth=4 expandtab smarttab:
