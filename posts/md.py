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
    def handleMatch(self, m):
        if m.group('inline'):
            return r'\(' + self.unescape(m.group('inline')).replace("\0292\03", '\\\\\\\\') + r'\)'
        else:
            return self.unescape(m.group('display')).replace("\0292\03", '\\\\\\\\')

unsafe_parser = markdown.Markdown(extensions=[Texer(), 'footnotes', 'smartypants'])
safe_parser = markdown.Markdown(safe_mode='escape', extensions=['smartypants', Nofollow(), Texer()])
