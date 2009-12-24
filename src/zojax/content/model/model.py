##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from BTrees.OOBTree import OOBTree

from zope import interface
from zope.schema import getFields
from zope.location import Location
from zope.component import getMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.app.pagetemplate import ViewPageTemplateFile

from interfaces import _, IViewModel, IViewModelExtension


class ViewModel(Location):
    interface.implements(IViewModel)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    @Lazy
    def __storage__(self):
        ext = getMultiAdapter(
            (self.context, self.request), IViewModelExtension, 'extension')
        data = ext.data.get(self.__id__)
        if data is None or not isinstance(data, OOBTree):
            if not isinstance(data, dict):
                data = {}
            data = OOBTree(data)
            ext.data[self.__id__] = data
        return data

    def update(self):
        pass

    def isAvailable(self):
        return True


def ViewModelType(name, class_=None, provides=(),
                  title='', description='', schema=None, **kw):

    cdict = {}
    cdict.update(kw)
    cdict['__id__'] = name
    cdict['__name__'] = name
    cdict['__schema__'] = schema
    cdict['__title__'] = title
    cdict['__description__'] = description

    class_name = 'ViewModel<%s>'%name

    if class_ is None:
        bases = (ViewModel,)
    else:
        bases = (class_, ViewModel)

    ViewModelClass = type(str(class_name), bases, cdict)

    if provides:
        interface.classImplements(ViewModelClass, *provides)

    if schema is not None:
        for f_id in getFields(schema):
            if not hasattr(ViewModelClass, f_id) and \
                   f_id not in ('context', 'request'):
                setattr(ViewModelClass, f_id, StorageProperty(schema[f_id]))

        interface.classImplements(ViewModelClass, schema)

    return ViewModelClass


_marker = object()

class StorageProperty(object):
    """ Special property thats reads and writes values from
    instance's 'data' attribute

    Let's define simple schema field

    >>> from zope import schema
    >>> field = schema.TextLine(
    ...    title = u'Test',
    ...    default = u'default value')
    >>> field.__name__ = 'attr1'

    Now we need content class

    >>> class Content(object):
    ...
    ...    attr1 = StorageProperty(field)

    Lets create class instance and add field values storage

    >>> ob = Content()
    >>> ob.__storage__ = {}

    By default we should get field default value

    >>> ob.attr1
    u'default value'

    We can set only valid value

    >>> ob.attr1 = 'value1'
    Traceback (most recent call last):
    ...
    WrongType: ('value1', <type 'unicode'>)

    >>> ob.attr1 = u'value1'
    >>> ob.attr1
    u'value1'

    delete value
    >>>
    >>> del ob.attr1
    >>> ob.attr1
    u'default value'

    If storage contains field value we shuld get it

    >>> ob.__storage__['attr1'] = u'value2'
    >>> ob.attr1
    u'value2'

    We can't set value for readonly fields

    >>> field.readonly = True
    >>> ob.attr1 = u'value1'
    Traceback (most recent call last):
    ...
    ValueError: ('attr1', u'Field is readonly')

    """

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        data = inst.__storage__
        if data is None:
            return self.__field.default

        value = data.get(self.__name, _marker)
        if value is _marker:
            return self.__field.default

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        field.validate(value)

        data = inst.__storage__

        if field.readonly and self.__name in data:
            raise ValueError(self.__name, _(u'Field is readonly'))

        data[self.__name] = value

    def __delete__(self, inst):
        data = inst.__storage__
        if data is not None:
            if self.__name in data:
                del data[self.__name]
