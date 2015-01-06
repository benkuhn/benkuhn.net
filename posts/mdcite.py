import markdown
from markdown.preprocessors import Preprocessor
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
from markdown.util import etree
import re

CIDENT_INITIAL_CHAR = r'[a-zA-Z_]'
CIDENT_CHAR = r'[a-zA-Z0-9_]'
CIDENT = '(?P<ident>' + CIDENT_INITIAL_CHAR + CIDENT_CHAR + '*)'
# only match citations that aren't part of emails by disallowing word chars
BARE_CITATION = '(?<=[^\w])@' + CIDENT

INLINE_BARE_CITATION = BARE_CITATION
NEWLINE_BARE_CITATION = '^@' + CIDENT

SOURCES_PLACEHOLDER = '///Sources Go Here///'

class CitationExtension(Extension):
    """Citation extension."""

    def reset(self):
        self.sources = {}

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        self.md = md

        md.preprocessors.add("citation", CitationPreprocessor(self), "<reference")

        md.inlinePatterns.add("citation1", CitationPattern(INLINE_BARE_CITATION, self, md), "<reference")
        md.inlinePatterns.add("citation2", CitationPattern(NEWLINE_BARE_CITATION, self, md), "<reference")

        # this has to go at the beginning for the block-parsing of sources to work
        md.treeprocessors.add("citation", CitationTreeprocessor(self), "_begin")

    def makeSourcesDiv(self):
        div = etree.Element("div")
        div.set('class', 'sources')

        sources = sorted(self.sources.values(), key=lambda source: source.short)

        for source in sources:
            p = etree.SubElement(div, 'div')
            p.set('class', 'source')
            p.set('id', source.get_id())
            self.md.parser.parseChunk(p, source.desc)

        return div

    def findPlaceholder(self, root):
        """ Return ElementTree Element that contains Footnote placeholder. """
        def finder(element):
            for child in element:
                if child.text:
                    if child.text.find(SOURCES_PLACEHOLDER) > -1:
                        return child, element, True
                if child.tail:
                    if child.tail.find(SOURCES_PLACEHOLDER) > -1:
                        return child, element, False
                finder(child)
            return None

        res = finder(root)
        return res



SOURCES_RE = re.compile(r'sources:', re.IGNORECASE)
SOURCE_SPEC_RE = re.compile(r'\s+' + CIDENT + ':\s+(?P<short>.*)')

class Source(object):

    def __init__(self, ident='', short='', desc=''):
        self.ident = ident
        self.short = short
        self.desc = desc

    def get_id(self):
        return 'source-' + self.ident

UNKNOWN_SOURCE = Source('unk', 'TODO unknown', 'TODO unknown. Lorem ipsum dolor sit amet.')

class CitationPreprocessor(Preprocessor):
    """Preprocessor that takes a block list of sources. The syntax is like:

    Sources:
      kl07: Karlan and List 2007
        Karlan, Dean and John List, 2007. Blahdeblah.
    """

    def __init__(self, citations):
        self.citations = citations

    def run(self, lines):
        new_lines = []
        sources_mode = False
        medium_indent = -1
        current_ident = None
        current_source = None
        for line in lines:
            if sources_mode:
                # have we figured out what the baseline indent is?
                indent = len(line) - len(line.lstrip())
                if medium_indent < 0:
                    medium_indent = indent
                if indent <= medium_indent:
                    m = SOURCE_SPEC_RE.match(line)
                    if not m:
                        continue
                    ident = m.group('ident')
                    short = m.group('short')
                    # finish off parsing the previous source
                    if current_ident is not None:
                        self.citations.sources[current_ident] = current_source
                    current_ident = ident
                    current_source = Source(ident=ident, short=short)
                else:
                    line = line.lstrip()
                    if current_source:
                        if current_source.desc:
                            current_source.desc += '\n' + line
                        else:
                            current_source.desc = line
            elif SOURCES_RE.match(line):
                sources_mode = True
            else:
                new_lines.append(line)
        if current_ident is not None:
            self.citations.sources[current_ident] = current_source
        return new_lines


class CitationPattern(Pattern):

    def __init__(self, regex, citations, markdown):
        Pattern.__init__(self, regex, markdown_instance=markdown)
        self.citations = citations

    def handleMatch(self, m):
        ident = m.group('ident')
        el = etree.Element("a")
        source = self.citations.sources.get(ident, UNKNOWN_SOURCE)
        el.set('href', '#' + source.get_id())
        el.text = markdown.util.AtomicString(source.short)
        return el


class CitationTreeprocessor(Treeprocessor):

    def __init__(self, citations):
        self.citations = citations

    def run(self, root):
        sourcesDiv = self.citations.makeSourcesDiv()
        if sourcesDiv:
            result = self.citations.findPlaceholder(root)
            if result:
                child, parent, isText = result
                ind = parent.getchildren().index(child)
                if isText:
                    parent.remove(child)
                    parent.insert(ind, sourcesDiv)
                else:
                    parent.insert(ind + 1, sourcesDiv)
                    child.tail = None
            else:
                root.append(sourcesDiv)
