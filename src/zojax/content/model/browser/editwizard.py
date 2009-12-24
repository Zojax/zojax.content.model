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
from zope.schema import getFieldNames
from zope.proxy import removeAllProxies
from zope.component import getAdapters, getMultiAdapter
from zope.security.checker import canWrite

from zojax.widget.radio import RadioWidgetFactory
from zojax.layoutform import button, Fields
from zojax.layoutform import PageletEditForm, PageletEditSubForm
from zojax.layoutform.interfaces import ICancelButton, ISaveAction

from zojax.extensions.interfaces import extensionMarker
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.model.interfaces import _, IViewModel, IViewModelExtension
from zojax.content.model.vocabulary import Models


class ContentModel(PageletEditForm):

    label = _(u'View model')
    fields = Fields(IViewModelExtension)
    prefix = 'content.model.'

    def update(self):
        self.content = self.context
        self.context = getMultiAdapter(
            (self.context, self.request, extensionMarker), IViewModelExtension)

        super(ContentModel, self).update()

    def isAvailable(self):
        voc = Models()(self.content)
        return len(voc) > 1


class ContentModelEdit(PageletEditForm):

    prefix = 'content.model.edit.'

    @property
    def label(self):
        return self.model.__title__

    @property
    def description(self):
        return self.model.__description__

    def getContent(self):
        return self.model

    def update(self):
        extension = getMultiAdapter(
            (removeAllProxies(self.context.getContent()),
             self.request, extensionMarker), IViewModelExtension)
        self.model = extension.getViewModel()
        self.schema = getattr(self.model, '__schema__', None)

        model = self.model
        self.avail = False
        if self.schema is not None:
            self.fields = Fields(self.schema)
            for name in getFieldNames(self.schema):
                if canWrite(model, name):
                    self.avail = True
                    break

        super(ContentModelEdit, self).update()

    def isAvailable(self):
        return self.avail

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                (self.formErrorsMessage,) + errors, 'formError')
        else:
            changes = self.applyChanges(data)
            if changes:
                IStatusMessage(self.request).add(self.successMessage)
            else:
                IStatusMessage(self.request).add(self.noChangesMessage)

            nextURL = self.nextURL()
            if nextURL:
                self.redirect(nextURL)

    @button.buttonAndHandler(_(u'Back'), name='back', provides=ICancelButton)
    def handleBack(self, action):
        self.redirect('./')
