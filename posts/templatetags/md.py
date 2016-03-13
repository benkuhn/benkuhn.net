from django import template
import posts.md
import md5, re
import datetime

register = template.Library()

@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist, safe=False)

@register.tag(name='usermarkdown')
def do_user_markdown(parser, token):
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
    tmp = posts.md.unsafe_parser.reset().convert(string)
    return stripper.sub('', tmp)

filters = [
    (re.compile(r'"([^\s])'), '&ldquo;\\1'),
    (re.compile(r'([^\s])"'), '\\1&rdquo;'),
    (re.compile(r"([^\s])'"), "\\1&rsquo;"),
    (re.compile(r"'([^\s])"), "&lsquo;\\1"),
    ]
@register.filter(name='quotify')
def quotify(string):
    for (regex, sub) in filters:
        string = regex.sub(sub, string)
    return string

spaces = re.compile('\s+')
@register.filter(name='deorphan')
def deorphan(string):
    split = spaces.split(string)
    if len(split) < 3:
        return string
    last2 = '&nbsp;'.join(split[-2:])
    return ' '.join(split[:-2] + [last2])

@register.filter(name='titlify')
def titlify(string):
    return deorphan(quotify(string))

@register.filter(name='fancydate')
def fancydate(dt):
    if dt.year < datetime.datetime.now().year:
        return dt.strftime('%B %Y')
    else:
        return dt.strftime('%B %-d')

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
