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
from zope import interface
from zope.component import getMultiAdapter, queryMultiAdapter

from zojax.layout.interfaces import IPagelet
from zojax.extensions.interfaces import extensionMarker
from zojax.content.type.interfaces import IContentView
from zojax.content.model.interfaces import IModelRenderer
from zojax.content.model.interfaces import IViewModelExtension


class ViewModelRenderer(object):

    modelView = None

    def __init__(self, context, request):
        super(ViewModelRenderer, self).__init__(context, request)

        extension = queryMultiAdapter(
            (context, request, extensionMarker), IViewModelExtension)

        view = extension.getViewModel()
        if view is not None and view.isAvailable():
            if IModelRenderer.providedBy(view):
                self.modelView = view
            else:
                self.modelView = queryMultiAdapter(
                    (view, request), IModelRenderer)

        if self.modelView is None:
            self.modelView = getMultiAdapter((context, request), IContentView)

    def update(self):
        if IPagelet.providedBy(self.modelView):
            self.modelView.update()

        if IContentView.providedBy(self.modelView):
            interface.alsoProvides(self, IContentView)

        super(ViewModelRenderer, self).update()

    def render(self):
        modelView = self.modelView
        if IPagelet.providedBy(modelView) or IModelRenderer.providedBy(modelView):
            return modelView.render()

        super(ViewModelRenderer, self).render()

    def __call__(self, *args, **kw):
        if IPagelet.providedBy(self.modelView):
            return self.modelView()

        return super(ViewModelRenderer, self).__call__()
