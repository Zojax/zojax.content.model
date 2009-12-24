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
from zope import schema, interface
from zope.component.zcml import handler
from zope.schema.interfaces import IField
from zope.configuration import fields
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.security.checker import defineChecker, Checker, CheckerPublic
from zope.app.security.protectclass import protectName, protectSetAttribute

from model import ViewModelType
from interfaces import IViewModel


class IViewModelDirective(interface.Interface):

    for_ = fields.GlobalObject(
        title = u"Context",
        description = u"The content interface or class this pagelet is for.",
        default = interface.Interface,
        required = False)

    name = fields.PythonIdentifier(
        title = u"Name",
        description = u"Name of the view model.",
        required = True)

    title = fields.MessageID(
        title = u"Title",
        description = u"Title of the model used in UIs.",
        required = True)

    description = fields.MessageID(
        title = u"Description",
        description = u"Description of the model used in UIs.",
        required = False)

    class_ = fields.GlobalObject(
        title = u"Class",
        description = u'Custom model class.',
        required = False)

    schema = fields.GlobalInterface(
        title = u"Schema",
        description = u'Model configuration schema.',
        required = False)

    layer = fields.GlobalObject(
        title = u'Layer',
        description = u'The layer for which the model should be available',
        required = False,
        default = IDefaultBrowserLayer)

    provides = fields.Tokens(
        title = u"The interface this model provides.",
        description = u"""This would be used for support other views.""",
        required = False,
        value_type = fields.GlobalInterface())


def viewModelDirective(
    _context, name, title, for_=interface.Interface, description=u'',
    class_=None, schema=None, layer=IDefaultBrowserLayer, provides=(), **kw):

    # Build a new class
    ViewModelClass = ViewModelType(
        name, class_, provides, title, description, schema, **kw)

    # Set up permission mapping for various accessible attributes
    required = {'__call__': CheckerPublic,
                'context': CheckerPublic,
                'request': CheckerPublic}

    for iname in IViewModel:
        required[iname] = CheckerPublic

    # security checker
    defineChecker(ViewModelClass, Checker(required))

    ifaces = list(provides)
    if schema is not None:
        ifaces.append(schema)

    # security for schema fields
    for iface in ifaces:
        for f_id in iface:
            field = iface[f_id]
            if IField.providedBy(field) and not field.readonly:
                protectSetAttribute(ViewModelClass, f_id, 'zojax.ManageViewModels')
            protectName(ViewModelClass, f_id, 'zope.Public')

    # register pagelet manager
    _context.action(
        discriminator = ('zojax:contentextensions.dynamic', name),
        callable = handler,
        args = ('registerAdapter',
                ViewModelClass, (for_, layer),
                IViewModel, name, _context.info))
