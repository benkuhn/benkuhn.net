from django import template
import posts.md
import md5, re

register = template.Library()

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

stripper = re.compile(r'<.*?>')
@register.filter(name='stripmd')
def stripmd(string):
    tmp = unsafe_parser.reset().convert(string)
    return stripper.sub('', tmp)

class MarkdownNode(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.nodelist = nodelist
        self.opts = kwargs
    def render(self, context):
        output = self.nodelist.render(context)
        if self.opts['safe']:
            parser = posts.md.safe_parser
        else:
            parser = posts.md.unsafe_parser
        return parser.reset().convert(output)
