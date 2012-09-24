import codecs
import datetime
import os
import re

from textile import textile
from mako.lookup import TemplateLookup
from pygments import formatters, lexers, highlight
from BeautifulSoup import BeautifulSoup, Tag

import config

class Post:
    def __init__(self, postfile, sitedir=config.sitedir, 
                 postdir=config.postdir, encoding=config.encoding):
        """Initializes a Post object with these fields: date, slug, body

           Arguments:
           :postfile: relative path to pyblee
           :encoding: string representation of encoding

        """
        self.sitedir = sitedir
        self.postdir = postdir
        self.encoding = encoding
        self.filename = os.path.split(postfile)[1]
       
        if re.match('((\d{2}-){3})', self.filename): # post or page? 
            y, m, d, H, M, self.slug = re.match(
                '(\d{2})-(\d{2})-(\d{2})-(\d{2}):(\d{2})-(.*)',
                self.filename).groups()
            date = datetime.datetime(int('20'+y),int(m),int(d), int(H), int(M))
            # lots of date formatting:
            (self.day, self.month, self.year)=(date.day, date.month, date.year)
            self.month_name = date.strftime('%B')
            self.pretty_date = date.strftime('%A, %B %e, %Y')
            self.pub_date = date.strftime("%a, %d %b %Y %H:%M GMT")
        else:
            self.slug = self.filename
       
        self.url = config.link + self.postdir + self.slug # + '.html'
        # read file
        f = codecs.open(postfile, 'r', encoding)
        try:
            postu = f.read()
        except UnicodeDecodeError:
            raise ValueError, 'your config.encoding is bogus %s' % postfile
        f.close()

        # get the post title and the body
        try:
            splits = postu.split('\n---\n\n')
            if len(splits) == 3:
                self.name, self.tags, self.body = splits
                self.tags = self.tags.split(', ')
            elif len(splits) == 2:
                self.name, self.body = splits
                self.tags = None
            else:
                raise ValueError, 'check formatting: '+ file
        except ValueError:
            raise ValueError, "check the formatting (I'd like a title "+  \
                              + 'and some tags, please!' + file

        self.body = self.highlight(self.markup(self.body))
        self.temp_lookup = TemplateLookup(directories=[config.templatedir], 
                                          default_filters=['decode.utf8'])

    def markup(self, body):
        """Uses textile to return a formatted unicode string"""
        soup = BeautifulSoup(body)
        preblocks = soup.findAll('pre')
        # add a <notextile> tag inside every pre lang tag
        for pre in preblocks:
            if pre.has_key('lang'):
                notextile_tag = Tag(soup, "notextile")
                notextile_tag.insert(0, pre.contents[0])
                pre.clear()
                pre.insert(0, notextile_tag)

        # textilize everything else
        return textile(unicode(soup))

    def highlight(self, body):
        """Syntax highlighting and textilization"""
        soup = BeautifulSoup(body)
        preblocks = soup.findAll('pre')

        formatter = formatters.HtmlFormatter()
        # highlight
        for pre in preblocks:
            if pre.has_key('lang'):
                lexer = lexers.get_lexer_by_name(pre['lang'],
                                                 encoding=self.encoding)
                code = ''.join([str(item) for item in pre.contents])
                code_hl = BeautifulSoup(highlight(code, lexer, formatter))
                pre.contents = [code_hl]
                pre.name = 'div'
                del(pre['lang'])
                pre['class'] = lexer.name
        return unicode(soup)

    def write(self, all_posts, all_tags):
        """Output the processed post"""

        if self.filename == self.slug: # page
            db_post = open(self.sitedir+self.slug+'.html', 'w')
            db_post.write(self.template('page.html', all_posts, all_tags))
            print 'Page updated: '+self.name
        else:
            db_post = open(self.sitedir+self.postdir+self.slug+'.html', 'w')
            db_post.write(self.template('post.html', all_posts, all_tags))
            # move posts in the directories specific to their tags
            print 'Post added: '+self.name +' -- '+self.pretty_date
        db_post.close()

    def template(self, temp, all_posts, all_tags):
        """Returns the final html, ready to be rendered"""
        
        templ = self.temp_lookup.get_template(temp)
        return templ.render_unicode(posts = [self],
                                    tag_page=False,
                                    config=config,
                                    all_posts=all_posts,
                                    all_tags=all_tags).encode('utf-8')
