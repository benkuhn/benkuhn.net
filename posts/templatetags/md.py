from django import template
import markdown
import md5
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension

register = template.Library()

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
        md.inlinePatterns['texer'] = TeXPattern()

class TeXPattern(Pattern):
    def __init__(self):
        Pattern.__init__(self, r'\$(?P<math>[^\s](.*[^\s]))\$')
    def handleMatch(self, m):
        return r'\(' + m.group('math') + r'\)'

@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist, safe=False)

@register.tag(name='usermarkdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endusermarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist, safe=True)

@register.filter(name='gravatar')
def gravatar(string):
    param = md5.md5(string).hexdigest()
    return 'http://www.gravatar.com/avatar/' + param

unsafe_parser = markdown.Markdown(extensions=['footnotes', 'smartypants'])
safe_parser = markdown.Markdown(safe_mode='escape', extensions=['smartypants', Nofollow(), Texer()])
class MarkdownNode(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.nodelist = nodelist
        self.opts = kwargs
    def render(self, context):
        output = self.nodelist.render(context)
        if self.opts['safe']:
            parser = safe_parser
        else:
            parser = unsafe_parser
        return parser.reset().convert(output)
