import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
import markdown
import re

class Nofollow(Extension):
    def extendMarkdown(self, md, md_globals):
        # Insert instance of 'mypattern' before 'references' pattern
        md.treeprocessors['nofollow'] = Cleaner()

class Cleaner(Treeprocessor):
    def run(self, root):
        for a in root.findall('.//a'):
            a.attrib['rel'] = 'nofollow'

class Texer(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['inlineMath'] = InlineMath(md)

class InlineMath(Pattern):
    def __init__(self, markdown):
        Pattern.__init__(self, r'((?P<display>\$\$[^\s](.*?[^\s])??\$\$)|\$(?P<inline>[^\s](.*?[^\s])??)\$(?=[^\d]|$))', markdown_instance=markdown)
    def argh(self, s):
        s = self.unescape(s)
        repls = (('92',  r'\\\\'),
                 ('123', r'\\{'),
                 ('125', r'\\}'))
        for needle, sub in repls:
            s = s.replace("\02%s\03" % needle, sub)
        return s
    def handleMatch(self, m):
        if m.group('inline'):
            return r'\(' + self.argh(m.group('inline')) + r'\)'
        else:
            return self.argh(m.group('display'))

URLIZE_RE = '(%s)' % '|'.join([
    r'<(?:f|ht)tps?://[^>]*>',
    r'\b(?:f|ht)tps?://[^)<>\s]+[^.,)<>\s]',
    r'\bwww\.[^)<>\s]+[^.,)<>\s]',
    r'[^(<\s]+\.(?:com|net|org)\b',
])

class UrlizePattern(markdown.inlinepatterns.Pattern):
    """ Return a link Element given an autolink (`http://example/com`). """
    def handleMatch(self, m):
        url = m.group(2)
        
        if url.startswith('<'):
            url = url[1:-1]
            
        text = url
        
        if not url.split('://')[0] in ('http','https','ftp'):
            if '@' in url and not '/' in url:
                url = 'mailto:' + url
            else:
                url = 'http://' + url
    
        el = markdown.util.etree.Element("a")
        el.set('href', url)
        el.set('rel', 'nofollow')
        el.text = markdown.util.AtomicString(text)
        return el

class UrlizeExtension(markdown.Extension):
    """ Urlize Extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Replace autolink with UrlizePattern """
        md.inlinePatterns['autolink'] = UrlizePattern(URLIZE_RE, md)


unsafe_parser = markdown.Markdown(extensions=[Texer(), 'footnotes', 'smartypants', 'toc'])
safe_parser = markdown.Markdown(safe_mode='escape', extensions=['smartypants', Nofollow(), Texer(), UrlizeExtension()])
