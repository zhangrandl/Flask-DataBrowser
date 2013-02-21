# -*- coding: UTF-8 -*-
import urllib
from flask import request
from flask.ext.databrowser.form.validators import Unique


def is_required_form_field(field):
    if not is_batch_edit():
        from wtforms.validators import Required
        for validator in field.validators:
            if isinstance(validator, Required):
                return True
    return False


def is_disabled_form_field(field):
    if is_batch_edit():
        for validator in field.validators:
            if isinstance(validator, Unique):
                return True
    return False


def is_batch_edit():
    return len(request.args.getlist("selected-ids")) > 1
