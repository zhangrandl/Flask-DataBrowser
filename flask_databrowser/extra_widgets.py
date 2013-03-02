"""
extra widgets beside wtform's widgets
"""
import operator
from wtforms.widgets import HTMLString, html_params
from wtforms.compat import text_type, string_types, iteritems
from flask.ext.databrowser.column_spec import ColumnSpec

class Image(object):
    def __init__(self, src, alt):
        self.src = src
        self.alt = alt

    # field is used here to compatiple with wtform's widgets
    def __call__(self, field, **kwargs):
        return HTMLString(
            '<a href="%s" class="fancybox control-text" rel="group" title="%s"><img '
            '%s /></a>' % (
            self.src, self.alt,
            html_params(src=self.src, alt=self.alt, **kwargs)))

class Link(object):

    def __init__(self, anchor, href):
        self.anchor = anchor
        self.href = href

    def __call__(self, field, **kwargs):
        return HTMLString('<a %s>%s</a>' % (html_params(href=self.href, **kwargs), self.anchor))

class PlainText(object):

    def __init__(self, s):
        self.s = s
    
    def __call__(self, field, **kwargs):

        return HTMLString('<span %s>%s</span>' % (html_params(**kwargs), self.s))

class TableWidget(object):

    def __init__(self, rows, col_specs=None):
        self.rows = rows
        self.col_specs = col_specs
        from flask.ext.databrowser.convert import ValueConverter
        self.converter = ValueConverter()

    def __call__(self, field, **kwargs):
        html = ['<table %s>\n' % html_params(**kwargs)]
        if self.rows:
            col_specs = self.col_specs or [ColumnSpec(col) for col in dir(self.rows[0]) if not col.startswith("_")]
            col_specs = [ColumnSpec(col) if isinstance(col, basestring) else col for col in col_specs]
            html.append('  <thead>\n%s\n  </thead>\n' % "\n".join(text_type(col.label).join(["    <th>", "</th>"]) for col in col_specs))
            # data rows
            for row in self.rows:
                s = "  <tr>\n"
                for sub_col_spec in col_specs:
                    s += "    <td>%s</td>\n" % self.converter(operator.attrgetter(sub_col_spec.col_name)(row), sub_col_spec)()
                s += "  </tr>\n"
                html.append(s)
        html.append('</table>')
        return HTMLString(''.join(html))

class ListWidget(object):

    def __init__(self, rows, col_spec, html_tag="ul"):
        self.rows = rows
        self.col_spec = col_spec
        self.html_tag = html_tag
        from flask.ext.databrowser.convert import ValueConverter
        self.converter = ValueConverter()

    def __call__(self, field, **kwargs):

        html = ["<%s>\n" % self.html_tag]
        for row in self.rows:
            html.append(" <li>%s</li>\n" % self.converter(row, self.col_spec)())
        html.append("</%s>" % self.html_tag)
        return HTMLString(''.join(html))

if __name__ == "__main__":
    print Image("http://a.com/a.jpg", "an image")(None)
    print Link("a.com", "http://a.com")(None)
    print PlainText("abc<123")(None)
    from collections import namedtuple
    from flask.ext.databrowser.column_spec import LinkColumnSpec, ImageColumnSpec, ColumnSpec
    table_column_spec = [LinkColumnSpec("a", "some link"), ImageColumnSpec("b"), ColumnSpec("c")]
    print TableWidget([namedtuple("A", ["a", "b", "c"])(i, i*2, i*3) for i in xrange(10)], ["a", "b", "c"])(None)
    print ListWidget([1, 2, 3], LinkColumnSpec(""))(None)
