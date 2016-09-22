# encoding: utf-8
"""
Definition of cell classes for the neuron module.

:copyright: Copyright 2006-2016 by the PyNN team, see AUTHORS.
:license: CeCILL, see LICENSE for details.

"""

import logging
from math import pi

from pyNN import errors
from pyNN.models import BaseCellType
from .recording import recordable_pattern
#from .simulator import state

try:
    reduce
except NameError:
    from functools import reduce

logger = logging.getLogger("PyNN")


def _new_property(obj_hierarchy, attr_name):
    """
    Returns a new property, mapping attr_name to obj_hierarchy.attr_name.

    For example, suppose that an object of class A has an attribute b which
    itself has an attribute c which itself has an attribute d. Then placing
      e = _new_property('b.c', 'd')
    in the class definition of A makes A.e an alias for A.b.c.d
    """

    def set(self, value):
        obj = reduce(getattr, [self] + obj_hierarchy.split('.'))
        setattr(obj, attr_name, value)

    def get(self):
        obj = reduce(getattr, [self] + obj_hierarchy.split('.'))
        return getattr(obj, attr_name)
    return property(fset=set, fget=get)


class NativeCellType(BaseCellType):

    def can_record(self, variable):
        # crude check, could be improved
        return bool(recordable_pattern.match(variable))

    # todo: use `guess_units` to construct "units" attribute



