#!/usr/bin/env python

"""usage: pyblee [-s|--sitedir=SITEDIR] [-d|--datadir=DATADIR]

Example usage:
    -t "Doomsday Clock" - sets the title
    -s 
"""

import sys
import getopt
import codecs

from BeautifulSoup import BeautifulSoup

from blog import Blog
from post import Post
from config import encoding, templatedir

def usage():
    print __doc__

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:d:s:", 
                ["title", "help", "datadir=", "sitedir="])
    except getopt.GetoptError, err:
        usage()
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ('-h','--help'):
            usage()
            sys.exit()
        elif opt in ('-t','--title'):
            # one-time modification of the template
            f = codecs.open(templatedir+'base.html', 'r', encoding)
            soup = BeautifulSoup(f.read())
            f.close()

            tag = soup.find('title')
            tag.contents[0].replaceWith(arg)

            tag = soup.find('a','title')
            tag.contents[0].replaceWith(arg)
            
            f = codecs.open(templatedir+'base.html','w',encoding)
            f.write(str(soup).decode(encoding))
            f.close()

            sys.exit('Title was set to:'+arg)

        elif opt in ('-d','--datadir'):
            datadir = arg
        elif opt in ('-s','--sitedir'):
            SITEDIR = arg
        else:
            assert False, "unhandled option"

    blog = Blog()
    
    for a in args:
        if a == 'update':
            blog.update()
        elif a == 'archive':
            blog.archive()
    if args == []:
        blog.update_all()

if __name__ == '__main__':
    main()
