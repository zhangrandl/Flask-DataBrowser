# -*- coding: UTF-8 -*-

# TODO need refactoring

from collections import namedtuple
import operator
from .utils import TemplateParam, raised_when, get_primary_key
from flask.ext.babel import gettext as _

_raised_when_model_unset = raised_when(lambda inst, *args, **kwargs: not inst.model_view, 
                                       RuntimeError(r'field "model view" unset, you should set it'))

class BaseFilter(TemplateParam):
    __notation__ = ""

    def __init__(self, col_name, name="", options=None, opt_formatter=None,
                 value=None, display_col_name=None):
        # TODO datetime unsupported
        self.op = namedtuple("op", ["name", "id"])(name, col_name + self.__notation__)
        self.col_name = col_name
        self.__display_col_name = display_col_name
        self.value = value
        self.model_view = None
        self.__options = options or []
        if self.__options and len(self.__options) > 1:
            self.__options.insert(0, (",".join(str(o[0]) for o in self.__options), u'--%s--' % _(u"所有")))
        self.opt_formatter = opt_formatter

    @property
    @_raised_when_model_unset
    def model(self):
        return self.model_view.model

    @property
    def label(self):
        return self.__display_col_name or self.model_view.__column_labels__.get(self.col_name, self.col_name)

    @property
    @_raised_when_model_unset
    def data_type(self):
        return 'numeric'

    @property
    @_raised_when_model_unset
    def input_type(self):
        if self.options:
            return "select"
        else:
            attr = getattr(self.model, self.col_name)
            if hasattr(attr, 'property'):
                col_type = type(attr.property.columns[0].type).__name__
                if col_type == 'Integer':
                    return 'number'
                else:
                    return 'text'

    @property
    @_raised_when_model_unset
    def input_class(self):
        return 'numeric-filter'

    @property
    def options(self):
        if self.__options:
            return self.__options
        else:
            # if column is a relation, then we should find all of them
            attrs = self.col_name.split(".")
            last_join_model = self.model
            for rel in attrs[:-1]:
                last_join_model = getattr(last_join_model, rel).property.mapper.entity
            attr = getattr(last_join_model, attrs[-1])
            ret = []
            if hasattr(attr, 'property') and hasattr(attr.property, 'direction'):
                model = attr.property.mapper.class_
                ret.extend((getattr(row, get_primary_key(model)), self.opt_formatter(row) if self.opt_formatter else row) 
                        for row in model.query.all())
            if len(ret) > 1:
                ret.insert(0, (",".join(unicode(r[0]) for r in ret), u'--%s--' % _(u"所有")))
            return ret


    def has_value(self):
        return self.value not in (None, "") and self.value != (self.options and self.options[0][0])

    def set_sa_criterion(self, q):
        """
        set the query filter/join criterions
        """
        attrs = self.col_name.split(".")
        last_join_model = self.model
        for attr in attrs[:-1]:
            last_join_model = getattr(last_join_model, attr).property.mapper.entity
            q = q.join(last_join_model)

        # convert attr to InstrumentedAttribute
        attr = getattr(last_join_model, attrs[-1])
        if hasattr(attr.property, 'direction'):
            # translate the relation
            filter_criterion = self.__operator__(enumerate(attr.property.local_columns).next()[1], self.value)
        else:
            filter_criterion = self.__operator__(attr, self.value)
        q = q.filter(filter_criterion)
        return q

    @property
    def sa_criterion(self):
        
        attr = getattr(self.model, self.col_name)
        if hasattr(attr.property, 'direction'):
            # translate the relation
            return self.__operator__(enumerate(attr.property.local_columns).next()[1], self.value)
        else:
            return self.__operator__(attr, self.value)

class EqualTo(BaseFilter):
    __notation__ = ""
    __operator__ = operator.eq

class NotEqualTo(BaseFilter):
    __notation__ = "__ne"
    __operator__ = operator.ne

class LessThan(BaseFilter):
    __notation__ = "__lt"
    __operator__ = operator.lt

class BiggerThan(BaseFilter):
    __notation__ = "__gt"
    __operator__ = operator.gt

class Contains(BaseFilter):
    __notation__ = "__contains"
    __operator__ = lambda self, attr, value: attr.like(value.join(["%", "%"]))