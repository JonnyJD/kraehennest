#!/usr/bin/python

#import cgitb
#cgitb.enable()

import cgi
from terrain import Terrain


if __name__ == '__main__':
    form = cgi.FieldStorage()
    print "Content-type: text/plain\n"

    if form.has_key("data"):
        terrain = Terrain()
        terrain.process(form["data"].value)
    else:
        terrain.process("")


# vim:set shiftwidth=4 expandtab smarttab:
