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
from rwproperty import setproperty, getproperty

from zope import interface, component
from zope.proxy import removeAllProxies
from zope.component import queryMultiAdapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zojax.content.browser.cache import ContentView
from zojax.content.type.interfaces import IContentView

from vocabulary import Models
from interfaces import IViewModel, IViewModelExtension, IViewModelSupport

models = Models()


class ViewModelExtension(object):
    interface.implements(IViewModelExtension)

    @getproperty
    def enabled(self):
        return IViewModelSupport.providedBy(self.context)

    @setproperty
    def enabled(self, value):
        context = removeAllProxies(self.context)
        if value:
            if not IViewModelSupport.providedBy(context):
                interface.alsoProvides(context, IViewModelSupport)
        else:
            if IViewModelSupport in interface.directlyProvidedBy(context):
                interface.noLongerProvides(context, IViewModelSupport)

    @getproperty
    def view(self):
        if not self.enabled:
            return u'__default__'
        else:
            return self.data.get('view', u'__default__')

    @setproperty
    def view(self, value):
        if value == '__default__':
            self.enabled = False
        else:
            self.enabled = True
            self.data['view'] = value

    def getViewModel(self):
        view = self.view
        if view == u'__default__':
            return None

        model = queryMultiAdapter((self.context, self.request), IViewModel, view)
        if model is not None:
            model.update()
            if model.isAvailable():
                return model

    def isAvailable(self):
        view = queryMultiAdapter((self.context, self.request), IContentView)
        if view is None:
            return False

        voc = models(self)
        if not bool(voc):
            return False

        return super(ViewModelExtension, self).isAvailable()


@component.adapter(IViewModelExtension, IObjectModifiedEvent)
def extensionModifiedHandler(ext, ev):
    ContentView.update(ext.context)


@component.adapter(IViewModel, IObjectModifiedEvent)
def viewmodelModifiedHandler(vm, ev):
    if hasattr(vm, 'context'):
        ContentView.update(vm.context)
