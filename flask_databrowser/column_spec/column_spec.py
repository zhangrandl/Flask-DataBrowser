# -*- coding: utf-8 -*-


class ColumnSpec(object):
    def __init__(self, col_name, doc=None,
                 formatter=None, label=None,
                 trunc=None, render_kwargs={}):
        self.col_name = col_name
        self.formatter = formatter
        self.doc = doc
        self.label = label
        self.trunc = trunc
        self.render_kwargs = render_kwargs

    @property
    def field(self):
        raise NotImplementedError


PlainTextColumnSpec = ColumnSpec  # alias to ColumnSpec
