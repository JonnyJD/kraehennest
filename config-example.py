"""Konfiguration der DB und Berechtigungen"""

import re
import os


debug = True            #: DEBUG-Ausgaben

# Datenbank
db_host = "localhost"   #: Hostname der Datenbank
db_user = ""            #: Benutzer der Datenbank
db_passwd = ""          #: Passwort der Datenbank
db = ""                 #: Name der Datenbank

preisdatei = '../preise'#: Ort der staendig aktualisierten Preisdatei

stunden_deaktivierung_1 = 48
tage_deaktivierung_2 = 7


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

def is_tester(username=None):
    """Ob der aktuelle (oder ein bestimmter) Benutzer Trunk testet

    @rtype: C{BooleanType}
    """
    return False

def is_kraehe(username=None):
    """Ob der aktuelle Benutzer (oder ein bestimmter) eine Kraehe ist

    @rtype: C{BooleanType}
    """
    if 'SCRIPT_URL' in os.environ:
        return not re.match("/tw", os.environ['SCRIPT_URL'])
    else:
        return False

def is_tw(username=None):
    """Ob der aktuelle Benutzer (oder ein bestimmter) ein TW ist

    @rtype: C{BooleanType}
    """
    if 'SCRIPT_URL' in os.environ:
        return re.match("/tw", os.environ['SCRIPT_URL'])
    else:
        return False

def allow_armeen(username=None, floating_message=False):
    return True

def allow_doerfer(username=None, floating_message=False):
    return True


# vim:set shiftwidth=4 expandtab smarttab:
