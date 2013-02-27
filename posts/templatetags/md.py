from django import template
import markdown

register = template.Library()

@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist)

parser = markdown.Markdown(safe_mode='escape', extensions=['footnotes', 'smartypants'])
class MarkdownNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        output = self.nodelist.render(context)
        return parser.reset().convert(output)
