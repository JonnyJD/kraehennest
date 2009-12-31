"""Konfiguration der DB und Berechtigungen"""

# Datenbank
db_host = "localhost"
db_user = ""
db_passwd = ""
db = ""

# Berechtigungen von logins
kraehen = []
tw = []

choose_kraehen = True

def is_kraehe(username):
    #return username in kraehen
    return choose_kraehen

def is_tw(username):
    #return username in tw
    return not choose_kraehen

# vim:set shiftwidth=4 expandtab smarttab:
