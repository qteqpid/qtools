from formatter import *
import htmllib
import StringIO
import urllib2
import chardet
import os, sys
import re
from lxml import etree
import lxml.html.soupparser

class Paragraph:
    def __init__ ( self ) :
        self.text = ''
        self.bytes = 0
        self.density = 0.0

class LineWriter( AbstractWriter) :
    def __init__ ( self , *args) :
        self.index = 0
        self.last_index = 0
        self.lines = [ Paragraph()]
        AbstractWriter.__init__ ( self )

    def send_flowing_data( self , data) :
#        print data
#        print self.index, self.last_index
        # Work out the length of this text chunk.
        t = len ( data)
        # We've parsed more text, so increment index.
        self.index += t
        # Calculate the number of bytes since last time.
        b = self.index - self.last_index
        self.last_index = self.index
        # Accumulate this information in current line.
        l = self.lines[ -1 ]
        l.text += data
        l.bytes += b

    def send_paragraph( self , blankline) :
        """Create a new paragraph if necessary."""
        if self.lines[ -1 ].text == '' :
            return
        self.lines[ -1 ].text += '\n' * ( blankline+1 )
        self.lines[ -1 ].bytes += 2 * ( blankline+1 )
        self.lines.append( Paragraph())

    def send_literal_data( self , data) :
        self.send_flowing_data( data)

    def send_line_break( self ) :
        self.send_paragraph( 0 )

    def compute_density( self ) :
        """Calculate the density for each line, and the average."""
        total = 0.0
        for l in self.lines :
            l.density = len ( l.text) / float ( l.bytes+1)
            total += l.density
        # Store for optional use by the neural network.
        self.average = total / float ( len ( self.lines))

    def output( self ) :
        """Return a string with the useless lines filtered out."""
        self.compute_density()
        output = StringIO.StringIO ()
        for l in self.lines :
            # Check density against threshold.
            # Custom filter extensions go here.
            #print l.density, l.bytes, l.text.decode('gb18030')
            if l.density > 0.5 and len(l.text) > 10:
                output.write( l.text)
        return output.getvalue()


class TrackingParser( htmllib.HTMLParser ) :
    """Try to keep accurate pointer of parsing location."""
    def __init__ ( self , writer, *args) :
        htmllib.HTMLParser.__init__ ( self , *args)
        self.writer = writer

    def parse_starttag( self , i) :
        index = htmllib.HTMLParser.parse_starttag( self , i)
        self.writer.index = index
#        print "s", self.writer.index
        return index

    def parse_endtag( self , i) :
        self.writer.index = i
#        print "e", self.writer.index
        return htmllib.HTMLParser.parse_endtag( self , i)


class Analyzer:
    def __init__(self):
        self.opener = None
        self.page_encoding = None
        self.p_body = re.compile('<body>.*</body>', re.DOTALL)
        self.p_script = re.compile('<script.*?</script>', re.DOTALL)
        self.p_style = re.compile('<style.*?</style>', re.DOTALL)
        self.p_style_1 = re.compile(' style="[^"].*"')
        self.p_badlink = re.compile('<a .*?</a>', re.DOTALL)
        self.p_comment = re.compile('<!--.*?-->', re.DOTALL)
        self.p_br = re.compile('<br.>')
        self.p_blank = re.compile('\s{2,}',re.DOTALL)

    def extract_text(self, html) :
        # Derive from AbstractWriter to store paragraphs.
        writer = LineWriter()
        # Default formatter sends commands to our writer.
        formatter = AbstractFormatter( writer)
        # Derive from htmllib.HTMLParser to track parsed bytes.
        parser = TrackingParser( writer, formatter )
        # Give the parser the raw HTML data.
        parser.feed( html)
        parser.close()
        # Filter the paragraphs stored and output them.
        return writer.output()

    def fetch(self, url):
        if not self.opener:
            self.opener = urllib2.build_opener()
        f = self.opener.open(url)
        page = f.read()
        self.page_encoding = chardet.detect(page)['encoding']
        return self.encode(page)

    def readfile(self, filename):
        f = open(filename, 'r')
        html = f.read()
        f.close()
        self.page_encoding = chardet.detect(html)['encoding']
        return self.encode(html)

    def encode(self, text):
        if self.page_encoding != None and self.page_encoding != 'gb18030':
            text = text.decode(self.page_encoding).encode('gb18030')
        return text

    def preprocess(self, text):
        body = self.p_body.search(text)
        if body == None: return text

        body = self.p_script.sub('', body.group())
        body = self.p_style.sub('', body)
        body = self.p_style_1.sub('', body)
        body = self.p_badlink.sub('>', body)
        body = self.p_comment.sub('', body)
        body = self.p_br.sub('', body)
        body = self.p_blank.sub(' ', body)
        return body

    def get_text(self, html):
        root = lxml.html.soupparser.fromstring(html)
        tags_to_ignore=["head", "style", "script", "noscript", "<built-in function comment>", "option"],
        tags_in_newline=["p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "br", "li"]
        def _get_text(tree):
            text = ''
            tag = str(tree.tag).lower()
            if (tag == '<built-in function comment>' or
               tag == 'style' or
               tag == 'script' or
               tag == 'noscript' or
               str(tree.tag).lower() in tags_to_ignore):
                return ''
            if tree.text != None:
                text += tree.text
            for child in tree:
                text += _get_text(child)
            if str(tree.tag).lower() in tags_in_newline:
                text += '\n'
            if tree.tail != None:
                text += tree.tail
            return text
        return _get_text(root)


if __name__=='__main__':
    if len(sys.argv) != 2:
        print "Usage: python extra.py page_url"
    else:
        ana = Analyzer()
        if sys.argv[1][0:4] == 'http':
            html = ana.fetch(sys.argv[1])
        else:
            if os.path.exists(sys.argv[1]):
                html = ana.readfile(sys.argv[1])
            else:
                print "File not found!"

        html = ana.preprocess(html)
        #print "Filter:", html

        html = ana.extract_text(html)
        print ana.get_text(html)

