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
from zope import interface, component, schema
from zope.security.proxy import removeSecurityProxy
from zojax.content.model.model import ViewModel
from zojax.content.model.interfaces import IModelRenderer
from zojax.content.type.interfaces import IContentView


class IMyDynamicView(interface.Interface):

    content = schema.TextLine(
        title = u'Content title',
        required = False)


class MyDynamicView(ViewModel):
    interface.implements(IModelRenderer, IContentView)
    component.adapts(interface.Interface, interface.Interface)

    def render(self):
        if self.content:
            return 'My Dynamic View: %s'%self.content
        else:
            return 'My Dynamic View: %s'%self.context.title


class IMyDynamicView2(interface.Interface):
    pass


class MyDynamicView2(ViewModel):
    component.adapts(interface.Interface, interface.Interface)


class MyDynamicView2View(object):

    def __call__(self, *args, **kw):
        return 'My Dynamic View: %s'%self.context.context.title
