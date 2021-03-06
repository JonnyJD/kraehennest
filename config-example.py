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

marked_reiche_color = "#000000" #: Markierungsfarbe

importkarte = True      #: ob die Importkarte angezeigt werden soll

def get_username():
    """Gebe den Namen des aktuell eingeloggten Benutzers zurueck.

    @rtype: C{StringType}
    """
    if 'REMOTE_USER' in os.environ:
        return os.environ['REMOTE_USER']
    else:
        return ""

def get_user_r_id(username=None):
    """Gebe die zugeordnete Reichsid eines Benutzers zurueck.

    @rtype: C{IntType}
    """
    return 0

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

def allow_details(username=None, message=True, floating_message=False):
    """Ob dem Benutzer Detail-Mouse-Overs angezeigt werden duerfen
    """
    return True

def allow_armeen(username=None, message=True, floating_message=False):
    """Ob dem Benutzer Armeen angezeigt werden duerfen
    """
    return True

def allow_armeen_all(username=None):
    """Ob dem Benutzer alle Armeen angezeigt werden duerfen
    """
    return True

def allow_armeen_ally(username=None):
    """Ob dem Benutzer Armeen der eigenen Allianz angezeigt werden duerfen
    """
    return True

def allow_armeen_own(username=None):
    """Ob dem Benutzer eigene Armeen angezeigt werden duerfen
    """
    return True

def allow_doerfer(username=None, message=True, floating_message=False):
    """Ob dem Benutzer Doerfer angezeigt werden duerfen
    """
    return True

def allow_hoehlen(username=None, message=True, floating_message=False):
    """Ob dem Benutzer Hoehlen angezeigt werden duerfen
    """
    return True

def allow_target(username=None):
    """Ob dem Benutzer {{{ziel}}}-Markierungen gezeigt werden duerfen
    """
    return True

def bounding_box(username=None):
    """Eine Box ueber die die angezeigte Karte nicht hinausgehen darf
    """
    # namedTuple nur ab python 2.6; sonst muss man ne Class machen
    #class Bounding_Box:
    #    def __init__(self, x1, y1, x2, y2):
    #        self.x1 = x1
    #        self.y1 = y1
    #        self.x2 = x2
    #        self.y2 = y2
    Bounding_Box = collections.namedtuple('Bounding_Box',
            ['x1', 'y1', 'x2', 'y2'])
    return Bounding_Box(x1=0, y1=0, x2=999, y2=999)


# vim:set shiftwidth=4 expandtab smarttab:
