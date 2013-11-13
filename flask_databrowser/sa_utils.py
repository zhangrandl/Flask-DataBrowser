# -*- coding: UTF-8 -*-
import operator
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.schema import Table


def is_relationship(model, col_name):
    return hasattr(operator.attrgetter(col_name)(model).property, 'direction')


def remote_side(col_def):
    return col_def.property.mapper.class_


def get_primary_key(model):
    """
        Return primary key name from a model

        :param model:
            Model class
    """
    if isinstance(model, Table):
        for idx, c in enumerate(model.columns):
            if c.primary_key:
                return c.key
    else:
        props = model._sa_class_manager.mapper.iterate_properties

        for p in props:
            if isinstance(p, ColumnProperty) and p.is_primary:
                return p.key

    return None


def get_joined_tables(model, col_name):
    result = []
    attrs = col_name.split(".")
    last_join_model = model
    for rel in attrs[:-1]:
        last_join_model = getattr(last_join_model, rel).property.mapper.class_
        result.append(last_join_model)
    return result

