"""Konfiguration der DB und Berechtigungen"""

import re
import os

# Datenbank
db_host = "localhost"   #: Hostname der Datenbank
db_user = ""            #: Benutzer der Datenbank
db_passwd = ""          #: Passwort der Datenbank
db = ""                 #: Name der Datenbank

def get_username():
    """Gebe den Namen des aktuell eingeloggten Benutzes zurueck.

    @rtype: C{StringType}
    """
    if 'REMOTE_USER' in os.environ:
        return os.environ['REMOTE_USER']
    else:
        return ""

def is_admin(username=None):
    """Ob der aktuelle (oder ein bestimmter) Benutzer Admin ist

    @rtype: C{BooleanType}
    """
    return False

def is_kraehe(username=None):
    """Ob der aktuelle Benutzer (oder ein bestimmter) eine Kraehe ist

    @rtype: C{BooleanType}
    """
    return not re.match("/tw", os.environ['SCRIPT_URL'])

def is_tw(username=None):
    """Ob der aktuelle Benutzer (oder ein bestimmter) ein TW ist

    @rtype: C{BooleanType}
    """
    return re.match("/tw", os.environ['SCRIPT_URL'])

# vim:set shiftwidth=4 expandtab smarttab:
