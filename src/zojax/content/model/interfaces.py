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
from zope.i18nmessageid import MessageFactory
from zojax.widget.radio.field import RadioChoice

_ = MessageFactory('zojax.content.model')


class IViewModel(interface.Interface):
    """ content view model """

    __name__ = interface.Attribute(u'Name')
    __title__ = interface.Attribute(u'Title')
    __description__ = interface.Attribute(u'Description')
    __schema__ = interface.Attribute(u'Storage schema')
    __storage__ = interface.Attribute(u'Storage')

    def isAvailable():
        """ is model available """

    def update():
        """ update model """


class IModelEdit(interface.Interface):
    """ model edit view """


class IModelRenderer(interface.Interface):
    """ model edit view """

    def render():
        """ render model """


class IViewModelSupport(interface.Interface):
    """ marker interface for content that support dynamic views """


class IViewModelExtension(interface.Interface):
    """ content view models extension """

    enabled = interface.Attribute('Is extension enabled')

    view = RadioChoice(
        title = _(u'View models'),
        description = _('List of all available view models.'),
        vocabulary = 'zojax.content.model-list',
        required = True)

    def getViewModel():
        """ get selected view model """
