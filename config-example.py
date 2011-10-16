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

stunden_deaktivierung_1 = 30    #: Stunden zur 1. Deaktivierung (Details?)
stunden_deaktivierung_2 = 48    #: Stunden zur 2. Deaktivierung (Armeen?)
tage_deaktivierung_3 = 7        #: Tage bis zur 3. Deaktivierung (Doerfer?)
tage_neu = 2                    #: Anzahl der Tage fuer den Layer "neu"

marked_reiche = []
"""auf der Karte zu markierende Reiche"""

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

def allow_details(username=None, floating_message=False):
    """Ob dem Benutzer Detail-Mouse-Overs angezeigt werden duerfen
    """
    return True

def allow_armeen(username=None, floating_message=False):
    """Ob dem Benutzer Armeen angezeigt werden duerfen
    """
    return True

def allow_doerfer(username=None, floating_message=False):
    """Ob dem Benutzer Doerfer angezeigt werden duerfen
    """
    return True

def allow_hoehlen(username=None, floating_message=False):
    """Ob dem Benutzer Hoehlen angezeigt werden duerfen
    """
    return True

def bounding_box(username=None):
    """Eine Box ueber die die angezeigte Karte nicht hinausgehen darf
    """
    Bounding_Box = collections.namedtuple('Bounding_Box',
            ['x1', 'y1', 'x2', 'y2'])
    return Bounding_Box(x1=0, y1=0, x2=999, y2=999)


# vim:set shiftwidth=4 expandtab smarttab:
